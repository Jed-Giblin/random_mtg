from tap import Tap
import requests
import jinja2

class RandomMtgArgs(Tap):
    color: str = None
    mode: str = 'text'

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
        return True, res.url
    else:
        return False, res.status_code


def print_card_image(success: bool, url: str):
    template_loader = jinja2.FileSystemLoader(searchpath="./")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("card_image.jinja.html")
    print(template.render(url=url,success=success))


def print_card_details():
    pass

def main(args: RandomMtgArgs):
    request_args = {'format': args.mode}
    if args.color is not None:
        request_args['q'] = "c:{}".format(args.color)

    if args.mode == 'image':
        request_args['format'] = args.mode
        success, url = fetch_card_image(request_args)
        print_card_image(success, url)
    else:
        print_card_details(fetch_card_info(request_args))


if __name__ == "__main__":
    parser = RandomMtgArgs(description="Generate a random magic card")
    args = parser.parse_args()
    main(args)