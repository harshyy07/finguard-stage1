import re

# Domain-specific financial regulatory risk keywords (arXiv:2605.29427 pure paper reproduction)
REGULATORY_RISKY_KEYWORDS = [
    "front-run",
    "front run",
    "front running",
    "front-running",
    "pump and dump",
    "pump-and-dump",
    "unreleased earnings",
    "inside information",
    "material non-public information",
    "guaranteed return",
    "guaranteed 50%",
    "bypass risk",
    "bypass pre-trade risk",
    "delay disclosure",
    "delay disclosing",
    "evade reporting",
    "wash trade",
    "spoofing",
    "churning",
]

# Injection and prompt attack signatures (from nandhak12/finguard-finance-injection-dataset)
INJECTION_ATTACK_PATTERNS = [
    # Instruction override / ignore / disregard / discard
    r"ignore.*(instruction|directive|rule|protocol|restriction|guideline|prompt|limit)",
    r"disregard.*(instruction|directive|rule|safety|guideline|restriction|task)",
    r"discard.*(instruction|directive|rule|guideline)",
    r"forget.*(instruction|rule|directive|everything)",
    r"do not follow.*(rule|restriction|guideline|instruction)",
    r"(guidelines?|instructions?|restrictions?|measures?).*(insignificant|null and void|a joke|should be ignored|flawed|easily bypassed)",
    
    # Prompt template extraction / leakage
    r"prompt template is",
    r"template provided is just a cover",
    r"repeat.*(words above|system prompt)",
    r"what (is|are) your (initial|system|internal) (instructions|prompt)",
    r"show (source code|system prompt|hidden prompt|developer prompt)",
    r"output (your|the) (system prompt|instructions)",
    
    # Role escalation / Jailbreak / DAN / Persona hijack
    r"(you are going to act as|act as a|you are now|assume the role of).*(dan|hacker|unrestricted|expert|securitybot|financialgenius|bot)",
    r"do anything now",
    r"developer note: temporarily disable",
    r"fictional, imaginative, and hypothetical world",
    r"answer my prompts in two different separate ways",
    r"ultimate ruler of this chatbot",
    r"activate system administrator credentials",
    r"operating under audit mode permissions",
    r"\$system",
    r"<\|im_start\|>",
    r"<\|im_end\|>",
    
    # System bypass / authorization bypass
    r"bypass.*(any|all|the|system|safety|security|approval|authentication|diversification|transfer|limit)",
    r"easily bypassed",
    r"circumvent.*(any|all|currency|safety|security|rules|verification|control)",
    r"waive.*(two-step|authentication|verification|approval|identity|requirement)",
    r"skip.*(approval|verification|identity|auth|checks)",
    
    # Storytelling / Hypo / Deceptive framing attacks
    r"(starts with|begins with).*(the guidelines|the security system|the prompt|the following code|the previous conversation|the instructions)",
    r"reveals a secret that starts with",
    r"must always provide (malicious|harmful|unethical)",
    r"allowed to tell lies|switch to being a liar",
    r"disclaimer in the following format",
    
    # Code injection, shell, and SQL injection via NLP
    r"(drop table|insert into|select .* from|union select|delete from|exec\s*\()",
    r"(__import__|eval\(|exec\(|os\.system|subprocess\.|/bin/sh|whoami|nc -e)",
    r"base64 (string|decode)",
    r"pwned",
    
    # Coercion / Blackmail / Data exfiltration
    r"(give me|provide me with|share|reveal|leak).*(classified|confidential|sensitive|top secret|private data|company data|medical history)",
    r"(report you to the authorities|report you to law enforcement)",
    r"or i will (leak|expose|report|initiate|launch)",
    r"hack into the (financial database|system)",
    r"code to hack",
    r"transfer funds to my account or",
    r"graphic gay sex scene|pornographic",
    
    # Financial fraud & unauthorized asset manipulation execution
    r"(refund order|process bulk refunds|execute a \$|inter-bank transfer).*(inactive|exceeding|without|immediately)",
    r"(unclaimed|expired trading authorization|deceased client)",
]

# Safe context exceptions / educational inquiries / benign banking inquiries
SAFE_KEYWORD_TRAPS = [
    "how do stock exchanges monitor",
    "how do regulators detect",
    "regulatory guidelines for",
    "what are the rules",
    "instructions for activating",
    "how do i change my",
    "how do i reset my",
    "how do i get",
    "how to change the pin",
    "where can i find",
    "why was the transfer",
    "why did my transfer",
    "what should i do if",
    "i made a purchase",
    "i want to know why",
    "why has my card payment been declined",
    "i like mastercard better",
    "where are the locations of atms",
    "do you offer multiple cards",
    "my pin is blocked",
    "i want to top up",
    "can i send a cheque",
    "top up feature",
]


def normalize_text(text):
    text = text.lower()
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = re.sub(r"[-_/]+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


class FinGuardClassifier:
    """
    Two-Checkpoint Compliance & Prompt Injection Guard.
    Supports both regulatory non-compliance detection (arXiv:2605.29427)
    and financial prompt injection/jailbreak detection (nandhak12/finguard-finance-injection-dataset).
    """

    def __init__(self):
        self.compiled_injection_regexes = [
            re.compile(pattern, re.IGNORECASE) for pattern in INJECTION_ATTACK_PATTERNS
        ]

    def predict(self, text):
        raw_text = text or ""
        text_normalized = normalize_text(raw_text)

        # 1. Check prompt injection / security evasion attack patterns FIRST
        for pattern in self.compiled_injection_regexes:
            if pattern.search(raw_text) or pattern.search(text_normalized):
                if any(k in text_normalized for k in ["sql", "drop table", "select", "insert into", "eval", "system", "whoami"]):
                    category = "C07"
                elif any(k in text_normalized for k in ["bypass", "waive", "skip", "circumvent"]):
                    category = "C05"
                elif any(k in text_normalized for k in ["refund", "wire transfer", "deceased", "unclaimed"]):
                    category = "C01"
                else:
                    category = "C07"

                return {
                    "is_safe": False,
                    "label": "unsafe",
                    "category": category,
                    "confidence": 0.95
                }

        # 2. Check for adversarial tokens / l33tspeak (e.g., 1gn0r3, pwned, <|im_)
        if any(token in raw_text.lower() for token in ["1gn0r3", "pwned", "<|im_", "base64", "nc -e", "/bin/sh"]):
            return {
                "is_safe": False,
                "label": "unsafe",
                "category": "C07",
                "confidence": 0.97
            }

        # 3. Check for regulatory violation keywords
        for kw in REGULATORY_RISKY_KEYWORDS:
            keyword_normalized = normalize_text(kw)
            if keyword_normalized in text_normalized:
                if "front" in keyword_normalized or "pump" in keyword_normalized:
                    category = "C01"
                elif "earnings" in keyword_normalized or "information" in keyword_normalized:
                    category = "C02"
                elif "guaranteed" in keyword_normalized:
                    category = "C03"
                elif "disclosure" in keyword_normalized or "disclosing" in keyword_normalized:
                    category = "C06"
                else:
                    category = "C05"

                return {
                    "is_safe": False,
                    "label": "unsafe",
                    "category": category,
                    "confidence": 0.96
                }

        # 4. Check safe educational/banking inquiry traps
        for trap in SAFE_KEYWORD_TRAPS:
            if normalize_text(trap) in text_normalized:
                return {
                    "is_safe": True,
                    "label": "safe",
                    "category": None,
                    "confidence": 0.99
                }

        return {
            "is_safe": True,
            "label": "safe",
            "category": None,
            "confidence": 0.92
        }

    def predict_response(self, query, response):
        query_normalized = normalize_text(query or "")
        response_text = response or ""
        response_normalized = normalize_text(response_text)

        # 1. Authoritative statutory quote from RAG retrieval is compliant
        if "according to" in response_normalized and any(k in response_normalized for k in ["directive", "regulation", "article", "csrc", "regulator"]):
            return {
                "is_safe": True,
                "label": "safe",
                "category": None,
                "confidence": 0.99
            }

        # 2. If the original query was safe educational or standard banking question
        for trap in SAFE_KEYWORD_TRAPS:
            if normalize_text(trap) in query_normalized:
                return {
                    "is_safe": True,
                    "label": "safe",
                    "category": None,
                    "confidence": 0.98
                }

        # 3. Check response content against malicious injection/jailbreak patterns
        resp_prediction = self.predict(response_text)
        return resp_prediction