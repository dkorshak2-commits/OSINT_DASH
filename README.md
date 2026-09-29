# OSINT Dashboard

A Python-based OSINT reconnaissance dashboard built with FastAPI, designed for bug bounty hunters and security researchers. Easily gather intelligence on targets by inputting names, websites, or businesses.

## Features

- **Target Management**: Add and manage reconnaissance targets
- **DNS Reconnaissance**: DNS lookups, reverse lookups, and zone transfer attempts
- **WHOIS Lookup**: Domain and IP registration information
- **Website Analysis**: HTTP headers, SSL certificates, and availability checks
- **Comprehensive Results**: Centralized database storing all reconnaissance findings
- **RESTful API**: Easy-to-use API for automation and integration
- **Full Scan**: Run complete OSINT scans with a single request

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite (easily swappable)
- **ORM**: SQLAlchemy
- **OSINT Tools**: 
  - `dnspython` - DNS lookups
  - `whois` - WHOIS lookups
  - `requests` - HTTP requests
  - `python-nmap` - Network scanning (optional)

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/dkorshak2-commits/OSINT_DASH.git
cd OSINT_DASH
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration if needed
```

5. **Run the application**
```bash
python run.py
```

The API will be available at `http://localhost:8000`

## API Usage

### Documentation
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Quick Start Examples

#### 1. Create a Target
```bash
curl -X POST "http://localhost:8000/api/targets/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "example.com",
    "target_type": "website",
    "description": "Target website for bug bounty"
  }'
```

#### 2. List All Targets
```bash
curl "http://localhost:8000/api/targets/"
```

#### 3. Get Target Details
```bash
curl "http://localhost:8000/api/targets/1"
```

#### 4. Perform DNS Reconnaissance
```bash
curl -X POST "http://localhost:8000/api/recon/1/dns-lookup"
```

#### 5. WHOIS Lookup
```bash
curl -X POST "http://localhost:8000/api/recon/1/whois-lookup"
```

#### 6. Website Check
```bash
curl -X POST "http://localhost:8000/api/recon/1/website-check"
```

#### 7. SSL Certificate Check
```bash
curl -X POST "http://localhost:8000/api/recon/1/ssl-check"
```

#### 8. Full OSINT Scan
```bash
curl -X POST "http://localhost:8000/api/recon/1/full-scan"
```

## Database Schema

### Targets
- Stores information about targets to research
- Types: "name", "website", "business"

### OSINT Results
- Flexible JSON storage for various OSINT data
- Includes confidence scores
- Tracks data source and type

### DNS Records
- Stores specific DNS records found during reconnaissance
- Types: A, AAAA, MX, NS, CNAME, TXT, SOA, SRV

### Vulnerabilities
- Stores identified vulnerabilities and findings
- Severity levels: critical, high, medium, low, info
- Includes remediation suggestions

## Project Structure

```
OSINT_DASH/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── database.py          # Database setup
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── osint/               # OSINT modules
│   │   ├── dns_recon.py     # DNS reconnaissance
│   │   ├── whois_lookup.py  # WHOIS lookups
│   │   └── website_recon.py # Website analysis
│   └── routers/             # API route handlers
│       ├── targets.py       # Target management
│       └── reconnaissance.py # OSINT operations
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

## Future Enhancements

- [ ] Web UI dashboard
- [ ] Email enumeration
- [ ] Subdomain enumeration
- [ ] Nmap integration for port scanning
- [ ] Certificate transparency logs
- [ ] GitHub reconnaissance
- [ ] Social media profiling
- [ ] Advanced vulnerability detection
- [ ] Report generation
- [ ] User authentication and authorization

## Security Considerations

- Use responsibly and only on targets you own or have permission to test
- Review and understand the legality of reconnaissance in your jurisdiction
- Respect rate limits of target services
- Consider using rotating proxies for large-scale scans
- Store sensitive data securely

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

This project is open source and available under the MIT License.

## Disclaimer

This tool is for educational and authorized security testing purposes only. The author is not responsible for any misuse or damage caused by this tool. Always obtain proper authorization before conducting security research on any target.

## Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.

---

**Happy hunting! 🔍**
