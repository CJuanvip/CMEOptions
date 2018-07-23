import subprocess


def get_addressees():
#    return ["bthrelkeld@rcgdirect.com"]
    return ["chathrel@indiana.edu"]


def send_mail(text, subject, attachment):
    addressees = get_addressees()
    for addressee in addressees:
        try:
            subprocess.run("echo \"{0}\" | mail -s \"{1}\" -A {2} {3}".format(text, subject, attachment, addressee), shell=True)
        except:
            pass
