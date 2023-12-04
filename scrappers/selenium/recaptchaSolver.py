from twocaptcha import TwoCaptcha


def recaptchaSolver(sitekey, url):
    API_KEY = "331b57cff358c0e42f3529ab52c8409b"
    solver = TwoCaptcha(API_KEY)

    try:
        result = solver.recaptcha(
            sitekey=sitekey,
            url=url
        )
    except Exception as e:
        print(e)
    else:
        return result
