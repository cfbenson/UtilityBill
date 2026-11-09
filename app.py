import base64
import io
import streamlit as st
from openai import OpenAI
from PIL import Image

# Page Configuration
st.set_page_config(
    page_title="Smart Utility Bill Calculator", 
    page_icon="⚡", 
    layout="wide"
)

st.title("⚡ Smart Utility Bill & Meter Calculator")
st.markdown(
    "Upload a past utility bill and a photo of your current meter to analyze "
    "your consumption rates and calculate your estimated charges up to today."
)

# Sidebar for OpenAI API Key configuration
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

def encode_image_to_base64(image: Image.Image) -> str:
    """Converts a PIL Image to a Base64-encoded JPEG string."""
    buffered = io.BytesIO()
    # Convert RGBA/Palette modes to RGB before saving as JPEG
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

if not api_key:
    st.info("👈 Please enter your OpenAI API key in the sidebar to get started.")
else:
    # Initialize OpenAI Client
    client = OpenAI(api_key=api_key)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Past Utility Bill")
        bill_file = st.file_uploader(
            "Upload bill image (Gas, Water, or Electric)", 
            type=["jpg", "jpeg", "png"]
        )
        if bill_file:
            bill_image = Image.open(bill_file)
            st.image(bill_image, caption="Uploaded Utility Bill", use_column_width=True)

    with col2:
        st.subheader("2. Current Meter Reading")
        meter_file = st.file_uploader(
            "Upload current meter photo", 
            type=["jpg", "jpeg", "png"]
        )
        if meter_file:
            meter_image = Image.open(meter_file)
            st.image(meter_image, caption="Current Meter Reading", use_column_width=True)

    # Calculation Trigger
    if bill_file and meter_file:
        st.divider()
        if st.button("Calculate Current Bill", type="primary", use_container_width=True):
            with st.spinner("Analyzing bill rates and reading current meter..."):
                try:
                    # Base64 encode both images for OpenAI API
                    bill_b64 = encode_image_to_base64(bill_image)
                    meter_b64 = encode_image_to_base64(meter_image)

                    prompt = """
                    You are an expert utility auditor and billing specialist. 
                    Examine the provided past utility bill image and the current meter reading image.
                    
                    Perform the following analysis:
                    1. **Bill Details:** Identify the utility type (Electric, Gas, or Water), billing period dates, previous meter reading, ending meter reading from the bill, total units consumed, and exact rate structure (fixed fees, tier rates per unit, taxes).
                    2. **Meter Reading:** Read the exact numbers shown on the current meter image.
                    3. **Consumption & Cost Calculation:**
                       - Calculate total units used between the bill's ending meter reading and the new meter reading.
                       - Estimate the days elapsed since the last bill.
                       - Calculate the estimated current bill amount using the rate structure found on the bill.
                    
                    Present your findings clearly in structured Markdown with headings and a summary table.
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{bill_b64}"
                                        },
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{meter_b64}"
                                        },
                                    },
                                ],
                            }
                        ],
                        max_tokens=1000,
                    )

                    st.success("Analysis Complete!")
                    st.markdown("### 📊 Consumption & Estimated Cost Breakdown")
                    st.markdown(response.choices[0].message.content)

                except Exception as e:
                    st.error(f"An error occurred during analysis: {e}")
