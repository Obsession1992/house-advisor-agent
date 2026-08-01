"""
Obsession · 刚需购房决策助手 v1.0
Streamlit Web 应用
专注老破小/二手房分析，帮首次购房者做出理性决策
"""
import streamlit as st
from PIL import Image
from core_logic import (
    calc_floor_score, calc_cost_base, calc_loan_cost,
    calc_rent_ratio, calc_buy_vs_rent, calc_land_share
)

# 页面配置
st.set_page_config(
    page_title="Obsession · 购房决策助手",
    page_icon="🏠",
    layout="wide"
)

# 自定义样式
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 5px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .danger-box {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 标题
st.title("🏠 Obsession · 刚需购房决策助手")
st.markdown("**毒舌但真诚的'懂行朋友'，帮首次购房者判断老破小/二手房是否值得买**")
st.markdown("---")

# ============ 侧边栏 - 输入表单 ============
with st.sidebar:
    st.header("📋 输入房产信息")

    # === 基本信息 ===
    st.subheader("🏘️ 基本信息")
    community_name = st.text_input(
        "小区名称 *",
        placeholder="例如：海狮沟、团结湖东里",
        help="用于推测物业/停车/周边环境"
    )

    col1, col2 = st.columns(2)
    with col1:
        current_floor = st.number_input(
            "所在楼层 *",
            min_value=1,
            value=1,
            help="当前所在楼层"
        )
    with col2:
        total_floors = st.number_input(
            "总楼层 *",
            min_value=1,
            value=6,
            help="建筑总楼层数（无电梯通常≤7）"
        )

    total_price = st.number_input(
        "挂牌总价（万元）*",
        min_value=1,
        value=200,
        help="二手房挂牌价格"
    )

    building_area = st.number_input(
        "建筑面积（㎡）*",
        min_value=1,
        value=73,
        help="房产证上的建筑面积"
    )

    # === 房屋详情 ===
    st.subheader("🔧 房屋详情")
    col3, col4 = st.columns(2)
    with col3:
        build_year = st.number_input(
            "建筑年代",
            min_value=1950,
            max_value=2026,
            value=1992,
            help="例如：1992"
        )
    with col4:
        renovation_year = st.number_input(
            "装修年份",
            min_value=1980,
            max_value=2026,
            value=None,
            help="最近一次装修年份"
        )

    far = st.number_input(
        "小区容积率",
        min_value=0.1,
        max_value=10.0,
        value=1.5,
        step=0.1,
        help="容积率越低，土地占有率越高。老小区通常1.2-1.5，高层2.5-3.5"
    )

    # === 财务参数 ===
    st.subheader("💰 财务参数")
    monthly_rent = st.number_input(
        "同小区月租金（元/月）*",
        min_value=500,
        value=5700,
        help="同面积同地段整租价格，可在贝壳/链家查看"
    )

    col5, col6 = st.columns(2)
    with col5:
        loan_ratio_pct = st.slider(
            "贷款比例",
            min_value=30,
            max_value=90,
            value=70,
            step=5,
            help="贷款占总价的比例"
        )
        loan_ratio = loan_ratio_pct / 100
    with col6:
        loan_rate = st.number_input(
            "年利率(%)",
            min_value=1.0,
            max_value=10.0,
            value=3.5,
            step=0.1,
            help="商贷利率，2025年首套约3.0-3.5%"
        ) / 100

    loan_years = st.selectbox(
        "贷款年限",
        [10, 15, 20, 25, 30],
        index=4,
        help="贷款期限"
    )

    st.markdown("---")

    # === 户型图 ===
    st.subheader("📐 户型图")
    uploaded_file = st.file_uploader(
        "上传户型图（可选）",
        type=['png', 'jpg', 'jpeg'],
        help="支持拍照或相册上传"
    )

# ============ 主区域 ============

# 构建用户输入
user_input = {
    'community_name': community_name,
    'current_floor': current_floor,
    'total_floors': total_floors,
    'total_price': total_price,
    'building_area': building_area,
}

# 计算所有模块
floor_info = calc_floor_score(current_floor, total_floors)
cost_info = calc_cost_base(build_year, renovation_year, building_area)
loan_info = calc_loan_cost(total_price, loan_ratio, loan_rate, loan_years)
rent_info = calc_rent_ratio(total_price, monthly_rent)
bvr_info = calc_buy_vs_rent(total_price, monthly_rent, loan_ratio, loan_rate, loan_years)
land_info = calc_land_share(building_area, far, total_floors)

if uploaded_file is not None:
    image = Image.open(uploaded_file)

# 布局：两列
main_col, side_col = st.columns([3, 1])

with side_col:
    # === 快速概览卡片 ===
    st.subheader("📊 关键指标速览")

    # 月供
    st.metric("月供", f"¥{loan_info['monthly_payment']:,.0f}")

    # 楼层评分
    st.metric("楼层评分", f"{'⭐' * floor_info['score']}{'☆' * (5 - floor_info['score'])}")

    # 租售比
    st.metric("租售比", f"1:{rent_info['rent_ratio']:.1f}",
              help=f"年化回报率 {rent_info['annual_return']*100:.2f}%")

    # 土地分摊
    st.metric("土地分摊面积", f"{land_info['land_share']:.1f}㎡",
              help=f"比27F高层多 {land_info['diff']}㎡")

    # 装修预算
    st.metric("装修预算", cost_info['cost_range'])

    # === 户型图显示 ===
    if uploaded_file is not None:
        st.markdown("---")
        st.image(image, caption="上传的户型图", use_column_width=True)

with main_col:
    # 生成报告按钮
    if st.button("🔍 生成完整决策报告", type="primary", use_container_width=True):
        if not community_name:
            st.error("请填写小区名称！")
        else:
            # ====== 第一部分：格局检测 ======
            st.markdown("---")
            st.header("🏠 一、格局硬伤检测")

            if uploaded_file is not None:
                st.info("📐 户型图已上传，以下为系统分析（v1.0基于规则，后续将接入AI识别）")
                # 这里预留AI户型分析接口
                st.markdown("""
                > 💡 **提示**：户型图AI识别功能即将上线（v2.0），届时将自动识别：
                > - 几室几厅几卫
                > - 朝向分析
                > - 暗卫/暗厨检测
                > - 动静分区评估
                > - 得房率估算
                """)
            else:
                st.warning("未上传户型图，格局分析跳过。上传户型图后可获得完整分析。")

            # ====== 第二部分：楼层评估 ======
            st.markdown("---")
            st.header("🪜 二、楼层与采光评估")

            score_display = '⭐' * floor_info['score'] + '☆' * (5 - floor_info['score'])
            st.markdown(f"**楼层评分：{score_display}**")
            st.markdown(f"**{floor_info['verdict']}**")

            if floor_info['warning']:
                st.markdown(f"""
                <div class="{'danger-box' if floor_info['score'] <= 2 else 'warning-box'}">
                    ⚠️ {floor_info['warning']}
                </div>
                """, unsafe_allow_html=True)

            if floor_info['elevator']:
                st.info("✅ 有电梯，日常出行方便。但注意：电梯房公摊面积大，得房率通常比板楼低10-15%。")
            else:
                st.info("📌 无电梯板楼。好处是得房率高（通常85%+），坏处是每天爬楼。")

            # ====== 第三部分：入住成本 ======
            st.markdown("---")
            st.header("💰 三、入住成本底线估算")

            st.markdown(f"**装修等级：{cost_info['level']}**")
            st.markdown(f"**估算费用：{cost_info['cost_range']}**")

            st.markdown(f"""
            <div class="info-box">
                🔧 {cost_info['advice']}
            </div>
            """, unsafe_allow_html=True)

            # ====== 第四部分：贷款利息 ======
            st.markdown("---")
            st.header("🏦 四、贷款利息深度分析")

            st.markdown(f"""
            **贷款条件：** 总价{total_price}万 | 首付{loan_info['down_payment']:.0f}万（{loan_ratio_pct}%） | 
            贷款{loan_info['loan_amount']:.0f}万 | 利率{loan_rate*100:.1f}% | {loan_years}年
            """)

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("月供", f"¥{loan_info['monthly_payment']:,.0f}")
            with col_b:
                st.metric("30年总利息", f"{loan_info['total_interest']:.1f}万")
            with col_c:
                st.metric("总还款", f"{loan_info['total_payment']:.1f}万")

            first_year_interest = loan_info['loan_amount'] * loan_rate
            first_month_interest = loan_info['loan_amount'] * 10000 * loan_rate / 12
            first_month_principal = loan_info['monthly_payment'] - first_month_interest

            st.markdown(f"""
            <div class="danger-box">
                <strong>🔴 你真正在"烧"的钱：</strong><br>
                • 你每月还的 ¥{loan_info['monthly_payment']:,.0f} 里，<br>
                • <strong>前5年</strong>：利息合计 {loan_info['first_5y_interest']:.1f}万，本金才 {loan_info['first_5y_principal']:.1f}万<br>
                • <strong>首年利息</strong>：约 {first_year_interest:.1f}万（占房价{first_year_interest/total_price*100:.1f}%）<br>
                • <strong>首月</strong>：利息 ¥{first_month_interest:,.0f}，本金只还 ¥{first_month_principal:,.0f}<br>
                • 30年总利息 <strong>{loan_info['total_interest']:.1f}万</strong>，相当于再买一套房的零头<br>
                <br>
                <strong>📊 买房每年真正消耗 = 利息 + 持有成本 ≈ {first_year_interest:.1f} + {bvr_info['holding_cost']:.1f} = {bvr_info['real_consumption']:.1f}万/年</strong>
            </div>
            """, unsafe_allow_html=True)

            # ====== 第五部分：租售比 ======
            st.markdown("---")
            st.header("📈 五、租售比与回本周期")

            col_d, col_e, col_f = st.columns(3)
            with col_d:
                st.metric("租售比", f"1:{rent_info['rent_ratio']:.1f}")
            with col_e:
                st.metric("年化回报率", f"{rent_info['annual_return']*100:.2f}%")
            with col_f:
                st.metric("纯靠租金回本", f"{rent_info['payback_years']:.0f}年")

            if rent_info['annual_return'] > 0.04:
                verdict_class = "success-box"
                verdict_emoji = "✅"
            elif rent_info['annual_return'] > 0.025:
                verdict_class = "info-box"
                verdict_emoji = "🔵"
            else:
                verdict_class = "warning-box"
                verdict_emoji = "⚠️"

            st.markdown(f"""
            <div class="{verdict_class}">
                {verdict_emoji} <strong>{rent_info['verdict']}</strong><br>
                同小区月租 ¥{monthly_rent:,} → 年租金 {rent_info['annual_rent']/10000:.1f}万<br>
                房价{total_price}万 ÷ 年租金{rent_info['annual_rent']/10000:.1f}万 = 租售比 1:{rent_info['rent_ratio']:.1f}<br>
                年化回报率 {rent_info['annual_return']*100:.2f}%
            </div>
            """, unsafe_allow_html=True)

            # ====== 第六部分：买房vs租房 ======
            st.markdown("---")
            st.header("🔀 六、买房 vs 租房 · 谁更亏？")

            comparison_data = {
                "项目": ["首付/押金", "月供/月租", "年支出", "其中'纯消耗'部分", "资金机会成本", "综合年成本"],
                "买房": [
                    f"{bvr_info['down_payment']:.0f}万",
                    f"¥{loan_info['monthly_payment']:,.0f}",
                    f"¥{bvr_info['annual_mortgage']*10000/12:,.0f}×12={bvr_info['annual_mortgage']:.1f}万",
                    f"{bvr_info['real_consumption']:.1f}万（利息{bvr_info['first_year_interest']:.1f}+持有{bvr_info['holding_cost']:.1f}）",
                    f"{bvr_info['opportunity_cost']:.1f}万（首付存银行的利息）",
                    f"<strong>{bvr_info['buy_annual_cost']:.1f}万</strong>"
                ],
                "租房": [
                    f"约{monthly_rent}×2={monthly_rent*2/10000:.1f}万",
                    f"¥{monthly_rent:,}",
                    f"¥{monthly_rent*12:,}={bvr_info['annual_rent']:.1f}万",
                    f"{bvr_info['annual_rent']:.1f}万（全部是纯消耗）",
                    f"无（首付{bvr_info['down_payment']:.0f}万存银行，年利息{bvr_info['opportunity_cost']:.1f}万）",
                    f"<strong>{bvr_info['rent_annual_cost']:.1f}万</strong>"
                ]
            }

            st.dataframe(
                {
                    "对比项": comparison_data["项目"],
                    "🏠 买房": comparison_data["买房"],
                    "🏘️ 租房": comparison_data["租房"],
                },
                use_container_width=True,
                hide_index=True,
            )

            diff = bvr_info['diff']
            if diff > 0:
                st.markdown(f"""
                <div class="warning-box">
                    <strong>📊 结论：买房每年多花 {diff:.2f}万</strong><br>
                    但买房的好处是：① 强制储蓄（每月还贷 = 存钱）② 学区/户口 ③ 不怕房东涨租赶人<br>
                    如果这{diff:.2f}万/年的差距你能接受，且有自住需求（学区/稳定感），那就买。<br>
                    如果纯粹投资角度，这个租售比不太划算。
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="success-box">
                    <strong>📊 结论：买房反而比租房省 {abs(diff):.2f}万/年！</strong><br>
                    这个价格买到就是赚到，租金回报率很不错。
                </div>
                """, unsafe_allow_html=True)

            # ====== 第七部分：土地占有率 ======
            st.markdown("---")
            st.header("🌍 七、隐藏优势：土地占有率")

            st.markdown(f"""
            这是大多数人忽略的维度 —— 你买的不只是房子，还有脚下那块地的份额。
            """)

            col_g, col_h, col_i = st.columns(3)
            with col_g:
                st.metric("你的土地分摊", f"{land_info['land_share']:.1f}㎡")
            with col_h:
                st.metric("27F高层对比", f"{land_info['ref_high_rise_land']}㎡")
            with col_i:
                st.metric("多出", f"{land_info['diff']}㎡（{land_info['ratio']:.1f}倍）")

            st.markdown(f"""
            <div class="success-box">
                <strong>🌍 土地占有率解读：</strong><br>
                • 你的房子：建面{building_area}㎡，容积率{far} → 每户分摊土地 <strong>{land_info['land_share']:.1f}㎡</strong><br>
                • 同等面积27F高层（容积率3.0）→ 每户仅分摊 {land_info['ref_high_rise_land']}㎡<br>
                • <strong>你多拿了 {land_info['diff']}㎡ 的土地份额，是高层的 {land_info['ratio']:.1f} 倍</strong><br>
                <br>
                💡 <strong>这意味着什么？</strong><br>
                • 未来拆迁补偿按土地面积算，你占优<br>
                • 低密度居住舒适度更高（绿化多、不压抑）<br>
                • 土地是不可再生资源，老小区的地段通常更好<br>
                • 拿到房产证时看一眼"土地分摊面积"，你会惊喜
            </div>
            """, unsafe_allow_html=True)

            # ====== 第八部分：三种出路 ======
            st.markdown("---")
            st.header("🔮 八、三种出路分析")

            st.markdown("""
            **买了之后，你大概率走这三条路：**
            """)

            # 出路1：自住到底
            st.markdown(f"""
            <div class="info-box">
                <strong>🏠 出路一：自住到底（5-10年+）</strong><br>
                • 每年"烧"掉 {bvr_info['real_consumption']:.1f}万（利息+持有成本）<br>
                • 但你有：稳定住所 + 学区 + 不怕涨租赶人<br>
                • 适合：刚需自住、有孩子上学需求、工作稳定<br>
                • <strong>关键指标</strong>：月供{loan_info['monthly_payment']:,.0f}元占月收入比例 < 50%？能扛住就行。
            </div>
            """, unsafe_allow_html=True)

            # 出路2：出租
            st.markdown(f"""
            <div class="info-box">
                <strong>🏘️ 出路二：出租（不住但持有）</strong><br>
                • 月租金 ¥{monthly_rent:,} → 年收 {rent_info['annual_rent']/10000:.1f}万<br>
                • 月供 ¥{loan_info['monthly_payment']:,.0f} × 12 = {loan_info['annual_mortgage']:.1f}万/年<br>
                • 每月净亏 ¥{loan_info['monthly_payment'] - monthly_rent:,.0f}（租金覆盖不了月供）<br>
                • 年化回报率 {rent_info['annual_return']*100:.2f}%，回本要 {rent_info['payback_years']:.0f}年<br>
                • <strong>结论</strong>：纯靠收租不划算，除非赌未来拆迁/升值
            </div>
            """, unsafe_allow_html=True)

            # 出路3：短期出手
            st.markdown(f"""
            <div class="{'warning-box' if total_floors <= 6 else 'info-box'}">
                <strong>💸 出路三：短期出手（3-5年卖掉）</strong><br>
                • 前5年还的贷款里，利息 {loan_info['first_5y_interest']:.1f}万，本金才 {loan_info['first_5y_principal']:.1f}万<br>
                • 加上契税、中介费、装修折旧，短期卖大概率亏<br>
                • 除非：① 房价短期大涨 ② 学区政策利好 ③ 拆迁消息<br>
                • <strong>结论</strong>：老破小不适合短期炒，适合长期持有
            </div>
            """, unsafe_allow_html=True)

            # ====== 第九部分：终极结论 ======
            st.markdown("---")
            st.header("🎯 九、终极结论")

            # 综合评分
            total_score = 0
            score_items = []

            # 楼层
            total_score += floor_info['score']
            score_items.append(f"楼层 {'⭐' * floor_info['score']}{'☆' * (5 - floor_info['score'])}")

            # 租售比评分
            if rent_info['annual_return'] > 0.04:
                rent_score = 4
            elif rent_info['annual_return'] > 0.025:
                rent_score = 3
            else:
                rent_score = 2
            total_score += rent_score
            score_items.append(f"租售比 {'⭐' * rent_score}{'☆' * (5 - rent_score)}")

            # 土地占有率评分
            if land_info['ratio'] > 1.5:
                land_score = 5
            elif land_info['ratio'] > 1.2:
                land_score = 4
            else:
                land_score = 3
            total_score += land_score
            score_items.append(f"土地占有率 {'⭐' * land_score}{'☆' * (5 - land_score)}")

            # 装修成本评分
            if cost_info['level'] == "基本入住":
                reno_score = 5
            elif cost_info['level'] == "微改":
                reno_score = 4
            elif cost_info['level'] == "中改":
                reno_score = 3
            else:
                reno_score = 2
            total_score += reno_score
            score_items.append(f"装修成本 {'⭐' * reno_score}{'☆' * (5 - reno_score)}")

            avg_score = total_score / 4

            if avg_score >= 4:
                verdict_text = "👍 值得买，性价比不错"
                verdict_color = "success-box"
            elif avg_score >= 3:
                verdict_text = "🤔 可以买，但有明显短板要注意"
                verdict_color = "info-box"
            else:
                verdict_text = "⚠️ 谨慎，建议多看几套对比"
                verdict_color = "warning-box"

            st.markdown(f"""
            <div class="{verdict_color}">
                <strong>{verdict_text}</strong><br><br>
                📊 综合评分：{'⭐' * round(avg_score)}{'☆' * (5 - round(avg_score))}（{avg_score:.1f}/5）<br><br>
                {'<br>'.join(['• ' + s for s in score_items])}<br><br>
                💰 每年真正消耗：<strong>{bvr_info['real_consumption']:.1f}万</strong>（利息+持有成本）<br>
                📈 租售比：1:{rent_info['rent_ratio']:.1f}（年化{rent_info['annual_return']*100:.2f}%）<br>
                🌍 土地分摊：{land_info['land_share']:.1f}㎡（比高层多{land_info['diff']}㎡）<br>
                🔧 入住成本：{cost_info['cost_range']}
            </div>
            """, unsafe_allow_html=True)

            # ====== 第十部分：行动建议 ======
            st.markdown("---")
            st.header("📌 十、下一步行动建议")

            st.markdown(f"""
            1. 🔍 **看房时带上乒乓球**：放地上看是不是往一边滚（测地面平整度）
            2. 🌡️ **问邻居冬天暖气热不热**：老小区暖气是命根子
            3. 🗺️ **打开地图搜"{community_name} 缺点"**：核实有没有垃圾站/高架桥/嫌恶设施
            4. 📋 **看房产证上的土地分摊面积**：这是你的隐藏资产
            5. 💰 **算清楚月供占收入比**：超过50%就要慎重
            6. 🏦 **去银行确认贷款资格**：老房子可能有房龄限制（通常房龄+贷款年限≤50年）
            7. 🏫 **确认学区政策**：如果是为了孩子上学，查清学位是否被占用
            """)

            st.markdown("---")
            st.markdown("*Obsession · 不吹不黑，只讲实话* | 数据仅供参考，实际以现场勘察为准")

    else:
        # 未操作时的引导
        st.markdown("### 👈 填写左侧信息，点击生成报告")
        st.markdown("""
        **报告包含以下十大模块：**
        1. 🏠 格局硬伤检测
        2. 🪜 楼层与采光评估
        3. 💰 入住成本底线估算
        4. 🏦 贷款利息深度分析
        5. 📈 租售比与回本周期
        6. 🔀 买房 vs 租房对比
        7. 🌍 土地占有率（隐藏优势）
        8. 🔮 三种出路分析
        9. 🎯 综合评分与终极结论
        10. 📌 下一步行动建议
        """)

# 页脚
st.markdown("---")
st.markdown("*Obsession · 刚需购房决策助手 v1.0* | 毒舌但真诚的懂行朋友")
