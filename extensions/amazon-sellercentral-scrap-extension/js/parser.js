class Parser {
    constructor() {
        this.parser = new DOMParser();
    }

    async parseDOM(htmlString) {
        try {
            return this.parser.parseFromString(htmlString, "text/html");
        } catch (error) {
            console.log(error);
        }
    }
}

export default Parser;