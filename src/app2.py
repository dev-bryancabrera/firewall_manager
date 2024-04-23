from flask import Flask

app = Flask(__name__)


def add_domain_to_hosts(domain):
    with open("/etc/hosts", "a") as hosts_file:
        hosts_file.write(f"127.0.0.1\t{domain}\n")


def remove_domain_from_hosts(domain):
    with open("/etc/hosts", "r") as hosts_file:
        lines = hosts_file.readlines()

    with open("/etc/hosts", "w") as hosts_file:
        for line in lines:
            if domain not in line:
                hosts_file.write(line)


@app.route("/add_rule", methods=["GET"])
def add_rule():
    domain = "www.tiktok.com"

    if domain:
        add_domain_to_hosts(domain)

        return "Rule added successfully", 200

    else:
        return "Domain parameter is required", 400


@app.route("/remove_rule", methods=["GET"])
def remove_rule():
    domain = "www.tiktok.com"

    if domain:
        remove_domain_from_hosts(domain)

        return "Rule removed successfully", 200

    else:
        return "Domain parameter is required", 400


if __name__ == "__main__":
    app.run(debug=True)
