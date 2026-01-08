# Quickstart: Beaver's Choice Paper Company Multi-Agent System

**Time to First Run**: ~10 minutes
**Prerequisites**: Python 3.8+, API key (OpenAI or Anthropic)

## 1. Environment Setup

### Clone and Navigate
```bash
cd /Users/felixalvez/Documents/80-projects/agentic-frameworks/uda-beaver
```

### Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies
```bash
pip install smolagents pandas sqlalchemy python-dotenv
```

### Configure API Key
Create a `.env` file in the project root:
```bash
# For OpenAI
OPENAI_API_KEY=sk-your-openai-key-here

# OR for Anthropic
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

## 2. Project Files

Ensure these files are in place:

```
uda-beaver/
├── beaver_agents.py           # You'll create this (main deliverable)
├── project-starter-ref-code/
│   ├── project_starter.py     # Helper functions (reference)
│   ├── quote_requests_sample.csv  # Test data (20 requests)
│   ├── quote_requests.csv     # Historical requests
│   └── quotes.csv             # Historical quotes
└── .env                       # Your API key (not committed)
```

## 3. Database Initialization

The database is initialized automatically when you run the system. The `init_database()` function from `project_starter.py`:
- Creates `munder_difflin.db` SQLite database
- Seeds $50,000 initial cash balance
- Loads ~18 products with initial stock (200-800 units each)
- Imports historical quotes and requests

## 4. Run the System

### Basic Execution
```bash
python beaver_agents.py
```

### Run Test Scenarios
The `run_test_scenarios()` function processes all 20 requests from `quote_requests_sample.csv`:
```bash
python beaver_agents.py
```

### Expected Output
```
Initializing Database...
=== Request 1 ===
Context: office manager organizing ceremony
Request Date: 2025-04-01
Cash Balance: $50000.00
Inventory Value: $XXX.XX

Response: Thank you for your order! For 200 sheets of A4 glossy paper...

Updated Cash: $50XXX.XX
Updated Inventory: $XXX.XX
...

===== FINAL FINANCIAL REPORT =====
Final Cash: $XXXXX.XX
Final Inventory: $XXXX.XX
```

## 5. Interactive Testing

For manual testing, modify `beaver_agents.py` to accept input:

```python
# At the bottom of beaver_agents.py
if __name__ == "__main__":
    init_database(db_engine)

    # Single request test
    request = "I need 500 sheets of glossy paper for a conference on April 15, 2025"
    response = orchestrator.run(request)
    print(response)
```

## 6. Verify Your Setup

Run this checklist before implementation:

- [ ] Python 3.8+ installed: `python --version`
- [ ] smolagents installed: `python -c "import smolagents"`
- [ ] API key configured: `python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OK' if os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY') else 'MISSING')"`
- [ ] Starter files present: `ls project-starter-ref-code/`
- [ ] No existing database: `rm -f munder_difflin.db` (clean start)

## 7. Common Issues

### "No module named 'smolagents'"
```bash
pip install smolagents
```

### "OPENAI_API_KEY not set"
Create `.env` file with your API key (see step 1).

### "sqlite3.OperationalError: no such table"
Database not initialized. Make sure `init_database(db_engine)` runs first.

### "Rate limit exceeded"
Add delays between requests or use a lower rate model.

## 8. Deliverables Checklist

After implementation, verify you have:

- [ ] `beaver_agents.py` - Single file with all agent code
- [ ] `workflow.png` - Agent diagram (export from Mermaid)
- [ ] `test_results.csv` - Output from test scenarios
- [ ] `docs/workflow.md` - Mermaid source for diagram
- [ ] Documentation explaining your design

## 9. Next Steps

1. **Implement agents**: Start with `beaver_agents.py`
2. **Test incrementally**: Run one request at a time
3. **Create diagram**: Use Mermaid (see constitution)
4. **Run full test suite**: Process all 20 scenarios
5. **Document**: Explain your design decisions

---

**Ready to implement?** Run `/speckit.tasks` to generate the implementation task list.
