class Email {
    constructor(login, domain, eid, sender, doAction) {
        this._login = login;
        this._domain = domain;
        this._eid = eid;
        this._sender = sender;
        this.doAction = doAction;
        this._data = null;
    }

    async fetchData() {
        try {
            const data = await this.doAction({
                "action": "readMessage",
                "login": this._login,
                "domain": this._domain,
                "id": this._eid
            });

            this._data = {
                'id': this._eid,
                'sender': this._sender,
                'body': data.body,
                'text': data.textBody,
                'html': data.htmlBody,
            };

            return this._data;
        } catch (e) {
            throw new Error(`Error have occurred while fetching Email[eid=${this._eid}] data: ${e.message}`);
        }
    }
}

class TempMail {
    constructor() {
        this.email = '';
        this.login = '';
        this.domain = '';
    }

    async genEmail() {
        try {
            const response = await fetch('https://www.1secmail.com/api/v1/?action=genRandomMailbox');
            const data = await response.json();
            this.email = data[0];
            [this.login, this.domain] = this.email.split('@');
        } catch (e) {
            throw new Error('Error have occurred while generating email: ' + e.message);
        }
    }

    async doAction(params) {
        const url = new URL('https://www.1secmail.com/api/v1/');
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
        const response = await fetch(url);
        return response.json();
    }

    async fetchEmails(from = null) {
        try {
            const dat = await this.doAction({
                "action": "getMessages",
                "login": this.login,
                "domain": this.domain
            });
            if (from) {
                return dat.filter(ml => ml.from.includes(from))
                    .map(ml => new Email(this.login, this.domain, ml.id, ml.from, this.doAction.bind(this)));
            }
            return dat.map(ml => new Email(this.login, this.domain, ml.id, ml.from, this.doAction.bind(this)));
        } catch (e) {
            throw new Error('Error have occurred while fetching emails: ' + e.message);
        }
    }
}

