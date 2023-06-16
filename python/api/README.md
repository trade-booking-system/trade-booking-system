## Useful Commands

### Setup Development Environment
```bash
python3 -m venv .venv
# enter the venv
pip install -r requrements_dev.txt
```

### Run Tests
```bash
pytest tests/
```

### Aggregate Positions
Aggregate positions for testing (replace accountName with actual name)
```bash
python scripts/aggregate.py accountName
```
Note: looks over all trades without considering dates
