import asyncio

import bottle
from bottle import request

from captcha_solver.solve_captcha_with_model import CaptchaSolver

capsolver = CaptchaSolver('captcha_solver')


async def run_bottle():
    @bottle.route('/solve/url', 'POST')
    def solve_url():
        return bottle.HTTPResponse(status=200, body=capsolver.solve_from_url(request.forms.get('url')))

    bottle.run(port=8090)


asyncio.run(run_bottle())
