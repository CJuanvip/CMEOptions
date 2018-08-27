import subprocess


def get_addressees():
    return ["bthrelkeld@rcgdirect.com"]
#    return ["chathrel@indiana.edu"]
#    return ["chathrel@indiana.edu", "bthrelkeld@rcgdirect.com"]


def send_mail(text, subject, attachment):
    addressees = get_addressees()
    for addressee in addressees:
        print("Emailing {0} to {1}".format(attachment, addressee))
        try:
            subprocess.run("echo \"{0}\" | mail -s \"{1}\" -A {2} {3}".format(text, subject, attachment, addressee), shell=True)
        except:
            subprocess.run("echo \"{0}\" | mail -s \"Error sending email to {1}\" {2}".format("Could not send {0} to {1}".format(attachment, addressee), addressee, "chathrel@indiana.edu"))
