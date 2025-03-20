class KalodataUserLoginLogout {
    constructor(initialSettings) {
        this.fetchSettings = initialSettings || {};
    }

    login(username, password) {
        const data = {
            'scene': 'login',
            'loginMethod': 'EMAIL_PASSWORD',
            'tcCode': '',
            'email': username,
            'emailPassword': password,
        };

        return fetch('https://www.kalodata.com/user/login', {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json',
            },
            ...this.fetchSettings,
        });
    }

    logout() {
        return fetch('https://www.kalodata.com/user/logout', {
            method: 'POST',
        });
    }
}