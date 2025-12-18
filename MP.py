import streamlit as st
from datetime import datetime, time
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Margin Shortfall Penalty Checker",
    page_icon="⚠️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .penalty-card {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 5px solid #dc2626;
        margin: 1rem 0;
    }
    .safe-card {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 5px solid #059669;
        margin: 1rem 0;
    }
    .warning-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 5px solid #f59e0b;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #eff6ff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
    }
    .metric-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("⚠️ Margin Shortfall Penalty Checker")
st.markdown("### Check if your margin shortfall will attract penalty as per SEBI regulations")

# Information banner
st.markdown("""
<div class="info-box">
    <strong>📋 Key Information:</strong>
    <ul>
        <li><strong>Peak Margin System:</strong> Exchanges capture margin snapshots multiple times during the day</li>
        <li><strong>Penalty applies when:</strong> Shortfall is <strong>≥ ₹1 lakh</strong> OR <strong>≥ 10%</strong> of required margin</li>
        <li><strong>Two types of margins:</strong> Upfront margin (at trade entry) and Non-upfront margin (EOD/delivery margins)</li>
        <li><strong>Deadline for non-upfront margins:</strong> T+1 day by 11:59 PM</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Create tabs for different scenarios
tab1, tab2, tab3 = st.tabs(["💰 Basic Penalty Check", "📊 Multiple Shortfalls", "📚 Understand Penalties"])

with tab1:
    st.markdown("### Calculate Penalty for Single Instance")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 📝 Input Details")
        
        # Margin inputs
        margin_available = st.number_input(
            "Margin Available (Funds + Collateral)",
            min_value=0.0,
            value=368578.89,
            step=1000.0,
            format="%.2f",
            help="Total margin available in your account including cash and pledged securities"
        )
        
        margin_required = st.number_input(
            "Margin Required",
            min_value=0.0,
            value=5361689.21,
            step=1000.0,
            format="%.2f",
            help="Total margin required for your positions"
        )
        
        st.markdown("#### Select Penalty Rate")
        penalty_rate = st.radio(
            "Choose applicable penalty rate",
            options=[0.5, 1.0, 5.0],
            index=1,
            format_func=lambda x: f"{x}% - {'Minor violations' if x == 0.5 else 'Standard violations' if x == 1.0 else 'Severe/Repeated violations (>3 days or >5 instances/month)'}",
            help="5% penalty applies if shortfall continues for >3 consecutive days or >5 instances in a month"
        )
        
        # Additional context
        st.markdown("#### Additional Information (Optional)")
        consecutive_days = st.number_input(
            "Consecutive days of shortfall",
            min_value=0,
            max_value=10,
            value=0,
            help="Number of consecutive days this shortfall has occurred"
        )
        
        monthly_instances = st.number_input(
            "Total instances this month",
            min_value=0,
            max_value=30,
            value=0,
            help="Number of margin shortfall instances in current month"
        )
    
    with col2:
        st.markdown("#### 📊 Analysis Results")
        
        # Calculate shortfall
        shortfall = max(0, margin_required - margin_available)
        shortfall_percentage = (shortfall / margin_required * 100) if margin_required > 0 else 0
        
        # Display metrics
        metric_col1, metric_col2 = st.columns(2)
        
        with metric_col1:
            st.metric(
                "Margin Required",
                f"₹{margin_required:,.2f}"
            )
            st.metric(
                "Shortfall Amount",
                f"₹{shortfall:,.2f}",
                delta=f"-{shortfall_percentage:.2f}%" if shortfall > 0 else "No shortfall",
                delta_color="inverse"
            )
        
        with metric_col2:
            st.metric(
                "Margin Available",
                f"₹{margin_available:,.2f}"
            )
            st.metric(
                "Shortfall %",
                f"{shortfall_percentage:.2f}%",
                delta="Above threshold" if shortfall_percentage >= 10 else "Below threshold",
                delta_color="inverse" if shortfall_percentage >= 10 else "normal"
            )
        
        # Determine if penalty applies
        is_penalty_by_amount = shortfall >= 100000
        is_penalty_by_percentage = shortfall_percentage >= 10
        is_penalty_applicable = is_penalty_by_amount or is_penalty_by_percentage
        
        # Auto-adjust penalty rate for severe violations
        effective_penalty_rate = penalty_rate
        if consecutive_days > 3 or monthly_instances > 5:
            effective_penalty_rate = 5.0
            st.warning(f"⚠️ Penalty rate automatically increased to 5% due to {'consecutive violations' if consecutive_days > 3 else 'multiple monthly instances'}")
        
        # Penalty status
        st.markdown("---")
        
        if shortfall == 0:
            st.markdown("""
            <div class="safe-card">
                <h3 style="color: #059669; margin-top: 0;">✅ No Penalty - Safe!</h3>
                <p style="margin-bottom: 0;">Your margin is sufficient. No shortfall detected.</p>
            </div>
            """, unsafe_allow_html=True)
        
        elif not is_penalty_applicable:
            st.markdown(f"""
            <div class="safe-card">
                <h3 style="color: #059669; margin-top: 0;">✅ No Penalty - Within Limits!</h3>
                <p><strong>Shortfall:</strong> ₹{shortfall:,.2f} ({shortfall_percentage:.2f}%)</p>
                <p style="margin-bottom: 0;"><strong>Reason:</strong> Shortfall is below both thresholds (< ₹1 lakh AND < 10%)</p>
            </div>
            """, unsafe_allow_html=True)
        
        else:
            # Calculate penalty
            penalty_on_shortfall = (effective_penalty_rate / 100) * shortfall
            gst_on_penalty = penalty_on_shortfall * 0.18
            total_penalty = penalty_on_shortfall + gst_on_penalty
            
            # Determine reason
            reasons = []
            if is_penalty_by_amount:
                reasons.append(f"Shortfall ≥ ₹1 lakh (₹{shortfall:,.2f})")
            if is_penalty_by_percentage:
                reasons.append(f"Shortfall ≥ 10% ({shortfall_percentage:.2f}%)")
            
            st.markdown(f"""
            <div class="penalty-card">
                <h3 style="color: #dc2626; margin-top: 0;">⚠️ PENALTY APPLICABLE</h3>
                <p><strong>Trigger Condition(s):</strong></p>
                <ul>
                    {''.join([f'<li>{reason}</li>' for reason in reasons])}
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Penalty breakdown
            st.markdown("### 💸 Penalty Calculation")
            
            penalty_col1, penalty_col2, penalty_col3 = st.columns(3)
            
            with penalty_col1:
                st.markdown(f"""
                <div class="metric-container">
                    <h4 style="color: #dc2626; margin: 0; font-size: 16px;">{effective_penalty_rate}% Penalty</h4>
                    <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #1f2937;">₹{penalty_on_shortfall:,.2f}</p>
                    <p style="color: #6b7280; font-size: 14px; margin: 0;">On shortfall amount</p>
                </div>
                """, unsafe_allow_html=True)
            
            with penalty_col2:
                st.markdown(f"""
                <div class="metric-container">
                    <h4 style="color: #dc2626; margin: 0; font-size: 16px;">18% GST</h4>
                    <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #1f2937;">₹{gst_on_penalty:,.2f}</p>
                    <p style="color: #6b7280; font-size: 14px; margin: 0;">On penalty amount</p>
                </div>
                """, unsafe_allow_html=True)
            
            with penalty_col3:
                st.markdown(f"""
                <div class="metric-container" style="background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); border: 2px solid #dc2626;">
                    <h4 style="color: #dc2626; margin: 0; font-size: 16px;">Total Penalty</h4>
                    <p style="font-size: 28px; font-weight: bold; margin: 10px 0; color: #dc2626;">₹{total_penalty:,.2f}</p>
                    <p style="color: #991b1b; font-size: 14px; margin: 0;">Amount payable</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Detailed breakdown
            st.markdown("#### Detailed Breakdown")
            breakdown_df = pd.DataFrame({
                "Description": [
                    "Margin Required",
                    "Margin Available",
                    "Shortfall Amount",
                    "Shortfall Percentage",
                    f"{effective_penalty_rate}% Penalty on Shortfall",
                    "18% GST on Penalty",
                    "Total Penalty"
                ],
                "Amount": [
                    f"₹{margin_required:,.2f}",
                    f"₹{margin_available:,.2f}",
                    f"₹{shortfall:,.2f}",
                    f"{shortfall_percentage:.2f}%",
                    f"₹{penalty_on_shortfall:,.2f}",
                    f"₹{gst_on_penalty:,.2f}",
                    f"₹{total_penalty:,.2f}"
                ]
            })
            st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

with tab2:
    st.markdown("### Track Multiple Shortfall Scenarios")
    st.info("💡 Penalty increases to 5% if shortfall continues for more than 3 consecutive days OR you have more than 5 instances in a month")
    
    # Example from the image
    st.markdown("#### Example: Multiple Shortfalls (As shown in your report)")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <h4>Margin Available</h4>
            <p style="font-size: 24px; font-weight: bold;">₹3,68,578.89</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Shortfall 1
        shortfall_1 = 5361689.21 - 368578.89
        shortfall_1_pct = (shortfall_1 / 5361689.21) * 100
        
        st.markdown(f"""
        <div class="penalty-card">
            <h4>Shortfall #1</h4>
            <p><strong>Margin Required:</strong> ₹53,61,689.21</p>
            <p><strong>Shortfall:</strong> ₹{shortfall_1:,.2f} ({shortfall_1_pct:.2f}%)</p>
            <p><strong>Deadline:</strong> 11:59 PM tonight</p>
            <p><strong>Status:</strong> ⚠️ Penalty Applicable (Both conditions met)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Shortfall 2
        shortfall_2 = 5163317.05 - 368578.89
        shortfall_2_pct = (shortfall_2 / 5163317.05) * 100
        
        st.markdown(f"""
        <div class="penalty-card" style="margin-top: 65px;">
            <h4>Shortfall #2</h4>
            <p><strong>Margin Required:</strong> ₹51,63,317.05</p>
            <p><strong>Shortfall:</strong> ₹{shortfall_2:,.2f} ({shortfall_2_pct:.2f}%)</p>
            <p><strong>Deadline:</strong> 9:14 AM tomorrow</p>
            <p><strong>Status:</strong> ⚠️ Penalty Applicable (Both conditions met)</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### Calculate Combined Penalty")
    
    # Calculate penalties for both
    penalty_1 = (1.0 / 100) * shortfall_1
    gst_1 = penalty_1 * 0.18
    total_1 = penalty_1 + gst_1
    
    penalty_2 = (1.0 / 100) * shortfall_2
    gst_2 = penalty_2 * 0.18
    total_2 = penalty_2 + gst_2
    
    grand_total = total_1 + total_2
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Shortfall #1 Penalty", f"₹{total_1:,.2f}")
    with col2:
        st.metric("Shortfall #2 Penalty", f"₹{total_2:,.2f}")
    with col3:
        st.metric("Total Combined Penalty", f"₹{grand_total:,.2f}", delta="Total payable", delta_color="inverse")
    
    # Action items
    st.markdown("""
    <div class="warning-card">
        <h4>⚡ Immediate Actions Required</h4>
        <ul>
            <li><strong>Add funds immediately</strong> to avoid penalties</li>
            <li><strong>Close positions</strong> to reduce margin requirement</li>
            <li><strong>Monitor deadlines:</strong> Different shortfalls have different deadlines</li>
            <li><strong>Avoid consecutive violations:</strong> Multiple days trigger 5% penalty</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.markdown("### 📚 Understanding Margin Penalties")
    
    # Penalty rate table
    st.markdown("#### Penalty Rate Structure")
    penalty_structure = pd.DataFrame({
        "Condition": [
            "Shortfall < ₹1 lakh AND < 10%",
            "Shortfall ≥ ₹1 lakh OR ≥ 10%",
            "Shortfall continues > 3 consecutive days",
            "More than 5 instances in a month"
        ],
        "Penalty Rate": [
            "0% - No Penalty",
            "0.5% to 1.0%",
            "5%",
            "5%"
        ],
        "GST": [
            "N/A",
            "18% on penalty",
            "18% on penalty",
            "18% on penalty"
        ]
    })
    st.dataframe(penalty_structure, use_container_width=True, hide_index=True)
    
    # Common scenarios
    st.markdown("#### Common Scenarios That Lead to Penalties")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Equity Trading:**
        - Intraday trade not squared off
        - Insufficient funds for delivery
        - Short delivery situations
        
        **F&O Trading:**
        - Margin increase due to position shuffling
        - One leg of hedged position expires
        - Physical delivery margins not maintained
        """)
    
    with col2:
        st.markdown("""
        **Both Segments:**
        - EOD margins not maintained
        - MTM losses not covered by T+1 day
        - Hedged position legs expire differently
        - Volatility-based margin increases
        - Ad-hoc margin requirements
        """)
    
    # How to avoid penalties
    st.markdown("""
    <div class="info-box">
        <h4>💡 How to Avoid Margin Penalties</h4>
        <ul>
            <li><strong>Maintain buffer:</strong> Keep 5-10% extra margin above requirement</li>
            <li><strong>Monitor regularly:</strong> Check margin requirements multiple times during trading day</li>
            <li><strong>Set alerts:</strong> Enable margin shortage notifications</li>
            <li><strong>Exit properly:</strong> Close highest margin position first in hedged trades</li>
            <li><strong>Plan ahead:</strong> Add funds before EOD if margin is tight</li>
            <li><strong>Watch expiry week:</strong> Physical delivery margins increase significantly</li>
            <li><strong>Use margin calculator:</strong> Always check margin before placing orders</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Important timelines
    st.markdown("#### ⏰ Important Timelines")
    timeline_df = pd.DataFrame({
        "Margin Type": [
            "Upfront Margin",
            "Non-Upfront Margin (MTM)",
            "Physical Delivery Margin",
            "Penalty Credit Date"
        ],
        "Timeline": [
            "At the time of placing order",
            "T+1 day by 11:59 PM",
            "4 days before expiry (progressive increase)",
            "T+6 days (reporting on T+5)"
        ],
        "Note": [
            "Must be available before trade execution",
            "For F&O MTM losses and margin increases",
            "10% → 25% → 45% → 70% of stock margin",
            "Penalty will reflect in ledger after 6 days"
        ]
    })
    st.dataframe(timeline_df, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; padding: 2rem 0;">
    <p><strong>References:</strong></p>
    <p>
        <a href="https://support.zerodha.com/category/trading-and-markets/margins/margin-reporting-and-margin-penalty/articles/margin-shortfall-instances" target="_blank">Zerodha: Margin Shortfall Instances</a> | 
        <a href="https://support.zerodha.com/category/trading-and-markets/margins/margin-reporting-and-margin-penalty/articles/i-saw-margin-penalty-entries-on-my-ledger-what-is-margin-penalty-and-why-have-i-been-charged" target="_blank">Zerodha: Margin Penalty Guide</a>
    </p>
    <p style="font-size: 14px; margin-top: 1rem;">⚠️ This calculator is for informational purposes only. Actual penalties may vary based on exchange regulations and specific circumstances.</p>
    <p style="font-size: 14px;">Always maintain sufficient margin and consult your broker for exact penalty calculations.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚡ Quick Reference")
    
    st.markdown("""
    **Penalty Triggers:**
    - ✗ Shortfall ≥ ₹1,00,000
    - ✗ Shortfall ≥ 10% of required margin
    - ✗ Either condition triggers penalty
    
    **Penalty Rates:**
    - 0.5% - Minor violations
    - 1.0% - Standard violations  
    - 5.0% - Severe (>3 days or >5 times/month)
    
    **Plus 18% GST on penalty**
    """)
    
    st.markdown("---")
    
    st.markdown("### 📱 Monitor Your Margins")
    st.info("""
    Check these regularly:
    - Kite Funds page
    - Console > Reports > Margin Report
    - Peak margin snapshots (4 times daily)
    """)
    
    st.markdown("---")
    
    st.markdown("### 🔗 Useful Tools")
    st.markdown("""
    - [Zerodha Margin Calculator](https://zerodha.com/margin-calculator/)
    - [Brokerage Calculator](https://zerodha.com/brokerage-calculator/)
    - [Support Portal](https://support.zerodha.com/)
    """)
    
    st.markdown("---")
    
    current_time = datetime.now().strftime("%I:%M %p")
    st.caption(f"Last updated: {current_time}")
    st.caption("Data based on SEBI & Exchange regulations")