from app.graph import graph
from app.state.state import EmailAgentState
import time
from psycopg import OperationalError

# Define your thread configuration
config = {"configurable": {"thread_id": "user_abc_123"}}


input_data: EmailAgentState = {
    "user_email_id":    "gaykaratharva7@gmail.com",
    "user_id":          1,
    "user_name":        "Atharva",
    "sender_email_id":  "atharvagaykar36@gmail.com",
    "sender_subject": "URGENT: Validation of Hybrid Phishing Detection Model & XGBoost Integration",
    "sender_email_body": """Dear Atharva,\r\n\r\nI have completed the integration of the *AI-Driven Email Threat Detection*\r\npipeline. We are currently utilizing the fine-tuned DistilBERT model to\r\ngenerate semantic embeddings for incoming messages.\r\n\r\nTo ensure the system is correctly identifying malicious intent, I've\r\nprocessed a suspicious sample using our custom structural tokens: [SSUB],\r\n[SBODY], [LINK], and [PHONE]. This preserves the email's structural context\r\nwhile protecting sensitive data.\r\n[MODEL EVALUATION DATA]\r\n\r\n*1. Semantic Context:* The fine-tuned DistilBERT has mapped the input to a\r\nhigh-dimensional vector space. Initial checks suggest strong clustering\r\nwith known phishing signatures.\r\n\r\n*2. URL Feature Engineering:* Our hybrid pipeline extracted numerical\r\nindicators from the embedded links.\r\n\r\n   -\r\n\r\n   Subdomain count: 4\r\n   -\r\n\r\n   Suspicious keywords: 2\r\n   -\r\n\r\n   Special characters: @, -, .\r\n   -\r\n\r\n   Redirection detected: True\r\n\r\n*3. XGBoost Classification:* The combined feature set (DistilBERT\r\nembeddings + numerical URL features) has been passed to the XGBoost\r\nclassifier.\r\n\r\n   -\r\n\r\n   *Current Test Accuracy:* 99.35%\r\n\r\nFinal Confirmation Needed:\r\n\r\n   1.\r\n\r\n   Should we deploy the current XGBoost weights to the:\r\n   https://huggingface.co/spaces/Gaykar/ClassifyEmail\r\n   2.\r\n\r\n   Do you want to review the Hybrid_model_preparation.ipynb logic before we\r\n   push to the:\r\n   https://github.com/Atharva-Gaykar/AI-Driven-Email-Threat-Detection\r\n   3.\r\n\r\n   Are the [LINK] and [PHONE] placeholders correctly masking the PII\r\n   (Personally Identifiable Information) according to the project spec?\r\n\r\nPlease provide your approval to proceed with the Docker deployment.\r\n\r\nBest regards,\r\n\r\nVinit Security AI Engineer\r\n"""
}




for i in range(3): # Try 3 times to account for Neon wake-up
    try:
        result = graph.invoke(input_data, config=config)
        break
    except OperationalError:
        print("Waiting for Neon to wake up...")
        time.sleep(5)


print(result)


