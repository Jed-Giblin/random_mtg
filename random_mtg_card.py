from tap import Tap
import requests
import jinja2
import shutil
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

class RandomMtgArgs(Tap):
    color: str = None
    mode: str = 'text'
    from_addr: str
    to_addr: str
    template_dir: str = './'

    def configure(self):
        self.add_argument('-c','--color',help="A color used to reduce the randomness")


def __get(url: str, params=dict, headers=dict) -> requests.Response:
    return requests.get(url, params=params, headers=headers)


def fetch_card_info(args: dict) -> tuple:
    res = __get('https://api.scryfall.com/cards/random', params=args, headers={'Content-Type':'application/json'})
    if res:
        return True, res.json()
    else:
        return False, res.status_code


def fetch_card_image(args):
    res = __get('https://api.scryfall.com/cards/random', params=args, headers={'Content-Type':'application/json'})
    if res.status_code < 400:
        filename = "./{}".format(res.url.split('/')[-1].split('?')[0])
        image = requests.get(res.url, stream=True)
        with open(filename, 'wb') as f:
            image.raw.decode_content = True
            shutil.copyfileobj(image.raw, f)
        return True, filename
    else:
        return False, res.status_code


def print_card_image(to_addr:str, from_addr:str, template_dir: str, success: bool, url: str):
    template_loader = jinja2.FileSystemLoader(searchpath=template_dir)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("card_image.jinja.html")
    body = template.render(url=url,success=success)
    message = MIMEMultipart()
    message['Subject'] = "MTG Card of the Day"
    message['From'] = from_addr
    message['To'] = to_addr
    message.attach(MIMEText(body, "html"))
    fp = open(url, 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()
    msgImage.add_header('Content-ID', '<image1>')
    message.attach(msgImage)
    import smtplib
    smtp = smtplib.SMTP()
    smtp.connect('localhost')
    smtp.sendmail(from_addr,to_addr, message.as_string())
    smtp.quit()


def print_card_details():
    pass


def main(args: RandomMtgArgs):
    request_args = {'format': args.mode}
    if args.color is not None:
        request_args['q'] = "c:{}".format(args.color)

    if args.mode == 'image':
        request_args['format'] = args.mode
        success, url = fetch_card_image(request_args)
        print_card_image(args.to_addr, args.from_addr, args.template_dir, success, url)
    else:
        print_card_details(fetch_card_info(request_args))


if __name__ == "__main__":
    parser = RandomMtgArgs(description="Generate a random magic card")
    args = parser.parse_args()
    main(args)