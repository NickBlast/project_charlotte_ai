## Request ChatGPT Data Export

It's time to request your monthly ChatGPT data export from OpenAI.

### Instructions

1. Visit the [OpenAI Privacy Portal](https://chat.openai.com/privacy)
2. Sign in to your account
3. Click "Export my data"
4. Wait for the email notification (usually 24-48 hours)
5. Download the ZIP file when it arrives
6. Process with the ingest tool:
   ```bash
   python tools/ingest_chatgpt_export.py --zip ~/Downloads/chatgpt-export.zip
   ```

### Why This Matters

Regular data exports help maintain:
- Complete conversation history
- Accurate memory candidates
- Up-to-date knowledge base
- Compliance with data retention policies

### After Export Processing

- Review memory candidates in `charlotte_ai/_intake/memory_candidates.md`
- Run diff proposer to generate patches
- Update relevant memory cards as needed

### Additional Resources

- [Charlotte Memory Pipeline Documentation](../docs/process/charlotte_memory_pipeline.md)
- [Ingest Tool Usage](../tools/ingest_chatgpt_export.py)
