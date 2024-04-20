import asyncio

import bottle
from bottle import request, HTTPError

from captcha_solver.solve_captcha_with_model import CaptchaSolver

capsolver = CaptchaSolver('captcha_solver')


async def run_bottle():
    @bottle.route('/solve/url/', 'POST')
    def solve_url():
        url = request.params.get('url') or request.forms.get('url')
        if not url:
            raise HTTPError(status=400, body='Bad Request')
        return bottle.HTTPResponse(status=200, body=capsolver.solve_from_url(url))

    bottle.run(host='0.0.0.0', port=8090)


asyncio.run(run_bottle())
