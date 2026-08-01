"""
核心计算逻辑模块
"""

def calc_floor_score(current_floor, total_floors):
    """
    楼层评分逻辑
    返回：评分(1-5)、楼层建议文本、警告信息
    """
    score = 3  # 默认中等
    verdict = ""
    warning = ""
    
    if total_floors <= 6:
        # 无电梯板楼
        if current_floor in [3, 4]:
            score = 5
            verdict = "金三银四，最佳楼层"
        elif current_floor == 5:
            score = 3
            verdict = "次优选择，爬楼可接受"
        elif current_floor == 6:
            score = 1
            verdict = "顶楼，冬冷夏热+漏水风险"
            warning = "顶楼警告：夏天像蒸笼，下雨天务必检查天花板有无水渍。每天爬楼就当健身，但买了大件快递你会哭。"
        elif current_floor <= 2:
            score = 2
            verdict = "低楼层，采光和隐私较差"
            warning = "低楼层采光可能受影响，蚊虫较多，隐私性差。"
        else:
            score = 3
            verdict = "普通楼层"
    else:
        # 有电梯塔楼
        mid_floor = total_floors // 2
        if mid_floor - 2 <= current_floor <= mid_floor + 2:
            score = 5
            verdict = "中高层，采光通风最佳"
        elif current_floor <= 3:
            score = 2
            verdict = "低楼层，挡光严重"
            warning = "低楼层采光可能受影响，等电梯时间长。"
        elif current_floor == total_floors:
            score = 2
            verdict = "顶楼，等电梯+顶楼通病"
            warning = "顶楼等电梯时间长，冬冷夏热风险。"
        else:
            score = 3
            verdict = "普通楼层"
    
    return {
        "score": score,
        "verdict": verdict,
        "warning": warning,
        "elevator": total_floors > 6
    }


def calc_cost_base(build_year, renovation_year, area_sqm):
    """
    装修成本估算
    返回：估算金额、装修建议
    """
    if renovation_year is None or renovation_year < 2010:
        # 老破小铁律：水电全改
        cost_per_sqm = 1500
        level = "全改"
        advice = "水电管线大概率已老化，建议水电全改+厨卫翻新+换窗。如果想省，至少把厨房卫生间砸了重做，其他刷墙凑合住。"
    elif renovation_year < 2015:
        # 中等翻新
        cost_per_sqm = 1000
        level = "中改"
        advice = "装修有一定年限，建议重点检查水电管线。厨房卫生间可能需要翻新，其他空间可以局部改造。"
    elif renovation_year < 2020:
        # 较新装修
        cost_per_sqm = 500
        level = "微改"
        advice = "装修相对较新，可以局部微改。重点检查水电是否正常，厨卫是否需要更新。"
    else:
        # 近期装修
        cost_per_sqm = 200
        level = "基本入住"
        advice = "近期装修，基本可以拎包入住。建议检查水电是否正常，必要时做深度清洁。"
    
    total_cost = area_sqm * cost_per_sqm
    cost_range = f"{total_cost * 0.8 / 10000:.1f}-{total_cost * 1.2 / 10000:.1f}万"
    
    return {
        "total_cost": total_cost,
        "cost_range": cost_range,
        "cost_per_sqm": cost_per_sqm,
        "level": level,
        "advice": advice,
        "build_year": build_year,
        "renovation_year": renovation_year
    }


def calc_loan_cost(total_price, loan_ratio=0.7, rate=0.035, years=30):
    """
    计算贷款利息成本
    返回：月供、总还款、总利息、各年本金/利息明细
    """
    loan_amount = total_price * 10000 * loan_ratio
    monthly_rate = rate / 12
    months = years * 12
    
    # 等额本息月供公式
    if monthly_rate > 0:
        monthly_payment = loan_amount * monthly_rate * (1 + monthly_rate)**months / ((1 + monthly_rate)**months - 1)
    else:
        monthly_payment = loan_amount / months
    
    total_payment = monthly_payment * months
    total_interest = total_payment - loan_amount
    
    # 前5年利息合计（近似）
    first_5y_interest = 0
    first_5y_principal = 0
    balance = loan_amount
    for m in range(60):
        interest_part = balance * monthly_rate
        principal_part = monthly_payment - interest_part
        first_5y_interest += interest_part
        first_5y_principal += principal_part
        balance -= principal_part
    
    return {
        "loan_amount": loan_amount / 10000,  # 万元
        "monthly_payment": monthly_payment,
        "total_payment": total_payment / 10000,  # 万元
        "total_interest": total_interest / 10000,  # 万元
        "first_5y_interest": first_5y_interest / 10000,  # 万元
        "first_5y_principal": first_5y_principal / 10000,  # 万元
        "down_payment": total_price * (1 - loan_ratio),  # 首付 = 总价 × (1-贷款比例)
    }


def calc_rent_ratio(total_price, monthly_rent):
    """
    计算租售比和回本周期
    total_price: 万元
    monthly_rent: 元/月
    """
    annual_rent = monthly_rent * 12
    rent_ratio = total_price * 10000 / annual_rent  # 租售比（年）
    annual_return = annual_rent / (total_price * 10000)  # 年化回报率
    
    if annual_return > 0.04:
        verdict = "租金回报率不错，出租划算"
    elif annual_return > 0.025:
        verdict = "租金回报率尚可，中规中矩"
    else:
        verdict = "租金回报率偏低，靠收租回本太慢"
    
    return {
        "monthly_rent": monthly_rent,
        "annual_rent": annual_rent,
        "rent_ratio": rent_ratio,
        "annual_return": annual_return,
        "payback_years": rent_ratio,
        "verdict": verdict
    }


def calc_buy_vs_rent(total_price, monthly_rent, loan_ratio=0.7, rate=0.035, years=30, risk_free_rate=0.03):
    """
    买房vs租房对比分析
    loan_ratio: 贷款比例（0.7表示贷70%，首付30%）
    """
    down_payment = total_price * (1 - loan_ratio)  # 首付
    loan_amount = total_price * loan_ratio  # 贷款额
    monthly_rate = rate / 12
    months = years * 12
    
    if monthly_rate > 0:
        monthly_payment = loan_amount * 10000 * monthly_rate * (1 + monthly_rate)**months / ((1 + monthly_rate)**months - 1)
    else:
        monthly_payment = loan_amount * 10000 / months
    
    annual_mortgage = monthly_payment * 12 / 10000  # 万/年
    
    # 首年利息
    first_year_interest = loan_amount * rate  # 万
    
    # 首年本金
    first_year_principal = annual_mortgage - first_year_interest
    
    # 持有成本（物业+维修，粗略估算）
    holding_cost = total_price * 0.0015  # 约房价的0.15%/年
    
    # 买房真消耗 = 利息 + 持有成本
    real_consumption = first_year_interest + holding_cost
    
    # 首付机会成本
    opportunity_cost = down_payment * risk_free_rate
    
    # 租房年成本
    annual_rent = monthly_rent * 12 / 10000  # 万/年
    
    # 综合年成本
    buy_annual_cost = real_consumption + opportunity_cost
    
    return {
        "down_payment": down_payment,
        "loan_amount": loan_amount,
        "annual_mortgage": annual_mortgage,
        "first_year_interest": first_year_interest,
        "first_year_principal": first_year_principal,
        "holding_cost": holding_cost,
        "real_consumption": real_consumption,
        "opportunity_cost": opportunity_cost,
        "annual_rent": annual_rent,
        "buy_annual_cost": buy_annual_cost,
        "rent_annual_cost": annual_rent,
        "diff": buy_annual_cost - annual_rent,
    }


def calc_land_share(building_area, far, total_floors=None):
    """
    计算土地分摊面积（土地占有率）
    building_area: 建筑面积（㎡）
    far: 容积率
    total_floors: 总楼层数（可选，用于对比展示）
    
    原理：土地分摊面积 ≈ 建筑面积 / 容积率
    低层老破小容积率低（1.2-1.5），每户分摊的土地面积大
    高层容积率（2.5-3.5+），每户分摊的土地面积小
    """
    if far <= 0:
        far = 1.5  # 默认容积率
    
    land_share = building_area / far  # ㎡
    
    # 对比参考：27F高层（容积率3.0）的土地分摊
    ref_high_rise_land = building_area / 3.0
    diff = land_share - ref_high_rise_land
    ratio = land_share / ref_high_rise_land if ref_high_rise_land > 0 else 1
    
    if total_floors and total_floors <= 6:
        building_type = "低层板楼"
    elif total_floors and total_floors <= 18:
        building_type = "中高层"
    elif total_floors and total_floors > 18:
        building_type = "高层塔楼"
    else:
        building_type = "未知"
    
    return {
        "land_share": land_share,
        "building_area": building_area,
        "far": far,
        "building_type": building_type,
        "ref_high_rise_land": round(ref_high_rise_land, 1),
        "diff": round(diff, 1),
        "ratio": round(ratio, 2),
    }


def generate_report_template(user_input, floor_info, cost_info, layout_info=""):
    """
    生成报告模板（不含LLM，纯规则版本）
    """
    report = f"""# 🔍 Obsession · 购房决策单

> 小区：{user_input['community_name']} ｜ {user_input['current_floor']}F/{user_input['total_floors']}F ｜ 总价：{user_input['total_price']}万

---

## 🏠 格局硬伤检测

{layout_info if layout_info else "（请上传户型图，我将分析格局硬伤）"}

---

## 🪜 楼层与采光评估

**楼层评分：** {'⭐' * floor_info['score']}{'☆' * (5 - floor_info['score'])}

{floor_info['verdict']}

{floor_info['warning'] if floor_info['warning'] else ''}

---

## 💰 入住成本底线估算

**估算费用：** {cost_info['cost_range']}

{cost_info['advice']}

---

## 🎯 值与不值 · 终极结论

（需要上传户型图后，综合分析给出结论）

---

## 📌 下一步行动建议

1. 下次看房，带个乒乓球放地上，看是不是往一边滚（测地面平整度）。
2. 问邻居冬天暖气热不热，老小区暖气是命根子。
3. 打开手机地图，搜"{user_input['community_name']} 缺点"，自行核实有没有垃圾站/高架桥噪音。

---

*Obsession · 不吹不黑，只讲实话*
"""
    return report
