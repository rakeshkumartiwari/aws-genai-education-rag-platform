# Architecture Notes

## Production AWS mapping
- Angular UI: Amazon S3 + Amazon CloudFront
- API layer: Amazon API Gateway
- Orchestration: AWS Lambda
- Foundation model: Amazon Bedrock
- Embeddings: Amazon Titan Embeddings or another Bedrock embedding model
- Vector database: Amazon OpenSearch Serverless vector engine
- Document storage: Amazon S3
- Monitoring: Amazon CloudWatch
- Security: IAM least privilege, KMS encryption, Bedrock Guardrails

## Request flow
1. Student asks a question in the web app.
2. API Gateway sends the request to Lambda.
3. Lambda checks safety rules and guardrails.
4. Lambda converts the question into an embedding.
5. OpenSearch returns the most relevant course chunks.
6. Lambda sends context plus question to Bedrock.
7. The model returns a grounded answer with sources.
8. CloudWatch captures latency, errors, and token usage metrics.

## Why RAG, not fine-tuning?
RAG is better here because course content changes often. With RAG, admins can update documents and re-index them. Fine-tuning would be slower, more expensive, and harder to govern for frequent content updates.
