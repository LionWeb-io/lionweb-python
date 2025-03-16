import os

code = f"""{{
  "server": {{
    "serverPort": 3005,
    "expectedToken": null
  }},
  "startup": {{
    "createDatabase": true,
    "createRepositories": [{{
        "name": "default",
        "history": false
      }}
    ]
  }},
  "logging": {{
    "request": "silent",
    "database": "silent",
    "express": "silent"
  }},
  "postgres": {{
    "database": {{
      "host": "{os.environ['PGHOST']}",
      "user": "{os.environ['PGUSER']}",
      "db": "{os.environ['PGDB']}",
      "password": "{os.environ['PGPASSWORD']}",
      "port": "{os.environ['PGPORT']}"
    }},
    "certificates": {{
      "rootcert": null,
      "rootcertcontent": null
    }}
  }}
}}
"""
with open("server-config.json", "w") as file:
    file.write(code)
