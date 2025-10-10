class DataModel {
    stringify() {
        const keys = Object.keys(this);
        return '{' + keys.reduce((acc, key) => {
            return acc + '"' + key + '": "' + this[key].replaceAll('"', '\\"') + '",';
        }).slice(0, -1) + '}';
    }
}