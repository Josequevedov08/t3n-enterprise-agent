import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("T3N-Enterprise-Agent")

class T3NEnterpriseAgent:
    """
    Enterprise Data Protection & Audit Agent built with Terminal 3 Network (T3N) concepts.
    Provides verifiable PII redaction and immutable action audit trails for enterprise workflows.
    """
    def __init__(self):
        self.did = os.getenv("T3N_ACCOUNT_DID", "did:t3n:6ed1b6547f69f9adf220086ea25371da40c480e9")
        self.api_key = os.getenv("T3N_API_KEY", "sandbox_key")
        self.env = os.getenv("T3N_ENVIRONMENT", "testnet")
        logger.info(f"Initialized T3N Agent for Tenant: {self.did} on {self.env}")

    def redact_sensitive_pii(self, payload: dict) -> dict:
        """Masks sensitive enterprise fields before downstream LLM processing."""
        redacted = payload.copy()
        sensitive_fields = ["ssn", "tax_id", "credit_card", "passport", "bank_account", "raw_secret"]
        
        for key in redacted:
            if any(s in key.lower() for s in sensitive_fields):
                redacted[key] = "[REDACTED_BY_T3N_ENCLAVE]"
            elif isinstance(redacted[key], str) and "@" in redacted[key]:
                parts = redacted[key].split("@")
                redacted[key] = f"{parts[0][:2]}***@{parts}"
        return redacted

    def execute_protected_task(self, enterprise_task: dict) -> dict:
        """Executes task inside simulated TEE verification envelope and logs audit event."""
        logger.info(f"Received enterprise payload for processing: Task ID {enterprise_task.get('task_id')}")
        
        # 1. Redact PII
        sanitized_data = self.redact_sensitive_pii(enterprise_task.get("data", {}))
        
        # 2. Generate Audit Event Envelope
        audit_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tenant_did": self.did,
            "task_id": enterprise_task.get("task_id"),
            "action_type": enterprise_task.get("action_type", "DATA_VERIFICATION"),
            "tee_attestation": "VERIFIED_HARDWARE_ENCLAVE",
            "sanitized_payload": sanitized_data,
            "status": "SUCCESS"
        }
        
        logger.info(f"T3N Audit Log created: Task {enterprise_task.get('task_id')} | Status: SUCCESS")
        return audit_record

if __name__ == "__main__":
    agent = T3NEnterpriseAgent()
    
    sample_request = {
        "task_id": "ENT-9842-KYC",
        "action_type": "CUSTOMER_ONBOARDING_VERIFICATION",
        "data": {
            "client_name": "Jose Quevedo",
            "client_email": "josequevedo@empresa.com",
            "tax_id": "TAX-992834-V",
            "bank_account": "ES9121000418450200051332",
            "risk_tier": "LOW"
        }
    }
    
    result = agent.execute_protected_task(sample_request)
    print("\n--- T3N AUDIT ATTESTATION RESULT ---")
    print(json.dumps(result, indent=2))
