import yaml,pyodbc,smtplib,jinja2,argparse
from email.mime.text import MIMEText


__author__ = 'chlr'

class EmailReporter:

    SMTP = { 'smtp': 'smtp.gmail.com:587'
             ,'username': 'myemail@gmail.com'
             ,'password': 'password'
           }

    TEMPLATE_PATH = 'templates'

    def __init__(self,config_file,title=None,description=None,template ='template.html'):
        self.rows = None
        self.fields = None
        self.template = template
        self.email,self.database = EmailReporter.read_config(config_file)
        self.title = title
        self.description = description

    @staticmethod
    def read_config(config_file):
        config = yaml.load(open(config_file))
        return config['email'],config['database']

    def execute_query(self):
        conn = pyodbc.connect(**dict(self.database['data_source']))
        cur = conn.cursor()
        self.rows = cur.execute(self.database['query']).fetchall()
        self.fields = [i[0] for i in cur.description]

    def send_email(self):
        self.execute_query()
        msg = MIMEText(self.construct_message(),'html')
        msg['To'] = self.email['to']
        msg['From'] = self.email['from']
        msg['Subject'] = self.email['subject']
        handle = smtplib.SMTP(EmailReporter.SMTP['smtp'])
        handle.starttls()
        handle.login(EmailReporter.SMTP['username'],EmailReporter.SMTP['password'])
        handle.sendmail(self.email['from'],self.email['to'],msg.as_string())

    def construct_message(self):
        tloader = jinja2.FileSystemLoader(searchpath=EmailReporter.TEMPLATE_PATH)
        env = jinja2.Environment(loader=tloader)
        template = env.get_template(self.template)
        bundle = { 'title':self.title
                  ,'description' : self.description
                  ,'fields' : self.fields
                  ,'rows' : self.rows }
        print(template.render(bundle))
        return template.render(bundle)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Email Reporter')
    parser.add_argument('-t','--title',default='',help='Title of the report')
    parser.add_argument('-d','--desc',default='',help='Description of the report')
    parser.add_argument('-c','--config',default='config.yml',help='Config file for the job')
    parser.add_argument('-f','--template',default='template.html',help='Config file for the job')
    settings =  parser.parse_args()
    email = EmailReporter(settings.config,title=settings.title,description=settings.desc,template=settings.template)
    email.send_email()






