class Dependency {
    main;
    depending;
    suffix = 'Id';

    constructor(main, depending) {
        this.main = main;
        this.depending = depending;
    }

    getDependency() {
        return this.depending;
    }

    getMainRelatedField() {
        return this.getDependency().name.toLowerCase() + this.suffix;
    }
}

class OneDep extends Dependency {
    suffix = 'Id';
}

class ManyDep extends Dependency {
    suffix = 'Ids';
}


class Creator {
    id;
    sellerId;
    shopIds;
    productIds;

    static create(id) {
        return {
            id,
            products: [1, 2],
            seller: 2,
            shops: [1, 2],
        };
    }

    constructor({ id, seller, shops, products }) {
        this.id = id;
        this.sellerId = seller;
        this.shopIds = shops;
        this.productIds = products;
    }
}

class Shop {
    id;
    creatorIds;
    videoIds;

    static create(id) {
        return {
            id,
            creators: [1, 2],
            videos: [1, 2],
        };
    }

    constructor({ id, creators, videos }) {
        this.id = id;
        this.creatorIds = creators;
        this.videoIds = videos;
    }
}

class Seller extends Shop {
    // No changes. It's just for new relation
}

class Product {
    id;
    sellerId;
    videoIds;

    static create(id) {
        return {
            id,
            seller: 1,
            videos: [1, 2],
        };
    }

    constructor({ id, seller, videos }) {
        this.id = id;
        this.sellerId = seller;
        this.videoIds = videos;
    }
}

class Video {
    id;
    productId;
    creatorId;

    static create(id) {
        return {
            id,
            product: 1,
            creator: 1,
        };
    }

    constructor({ id, creator, product }) {
        this.id = id;
        this.creatorId = creator;
        this.productId = product;
    }
}


class GraphDependencies {
    typesIndexesMap = new Map();
    dependencies = [];  // [ [(with 1 main and N depending)Dep1, Dep2, ...], ... ]

    // Format: [ {main: type, deps: {Type: DepType, ...}}, ... ]
    constructor(deps) {
        const depsTypesMap = [
            OneDep,
            ManyDep,
        ];
        for (const depMapItem of deps) {
            const indexes = [];
            for (const [dep, many] of depMapItem.deps.entries()) {
                indexes.push(this.dependencies.push(new depsTypesMap[Number(many)](depMapItem.main, dep)) - 1);
            }
            this.typesIndexesMap.set(depMapItem.main, [...indexes]);
        }
    }
}


class GraphFiller {
    graph;
    items = new Set();
    readyItems = new Set();
    res = new Map();

    constructor(graph) {
        this.graph = graph;
        for (const { main } of graph.dependencies) {
            this.items.add(main);
        }
    }

    fill(data, type) {
        this.readyItems.add(type);
        let rootItemObj = new type(data);
        if (!this.res.has(type)) {
            const objmap = new Map();
            objmap.set(rootItemObj.id, rootItemObj);
            this.res.set(type, objmap);
            if (rootItemObj.init) {
                rootItemObj.init();
            }
        } else {
            const objmap = this.res.get(type);
            if (objmap.has(data.id)) {
                return;
            }
            objmap.set(data.id, rootItemObj)
            if (rootItemObj.init) {
                rootItemObj.init();
            }
        }
        const depsIndexes = this.graph.typesIndexesMap.get(type);
        // console.log(type, rootItemObj, depsIndexes);
        let res = new Map();
        for (const depIndex of depsIndexes) {
            const dep = this.graph.dependencies[depIndex];
            const depType = dep.getDependency();
            if (this.readyItems.has(depType)) {
                continue;
            }
            const relatedField = dep.getMainRelatedField();
            const items = [];
            if (typeof rootItemObj[relatedField] === 'number') {
                res.set(depType, depType.create(rootItemObj[relatedField]));
            } else {
                // console.log(rootItemObj[relatedField], rootItemObj, relatedField);
                for (const id of rootItemObj[relatedField]) {
                    items.push(depType.create(id));
                }
                res.set(depType, items);
            }
        }
        return res.size ? res : null;
    }

    fillRecursive(data, type) {
        let res = this.fill(data, type);
        if (!res) {
            return null;
        }
        for (const [type, data] of res.entries()) {
            // console.log(type, data);
            if (data.length) {
                for (const datum of data) {
                    this.fillRecursive(datum, type);
                }
            } else {
                this.fillRecursive(data, type);
            }
        }
    }
}


// Example
const creatorDeps = new Map();
const productDeps = new Map();
const videoDeps = new Map();
const shopDeps = new Map();

creatorDeps.set(Shop, true);
creatorDeps.set(Seller, false);
creatorDeps.set(Product, true);

productDeps.set(Seller, false);
productDeps.set(Video, true);

shopDeps.set(Creator, true);
shopDeps.set(Video, true);

videoDeps.set(Creator, false);
videoDeps.set(Product, false);

const gd = new GraphDependencies([
    {
        main: Creator, deps: creatorDeps,
    },
    {
        main: Product, deps: productDeps,
    },
    {
        main: Shop, deps: shopDeps,
    },
    {
        main: Seller, deps: shopDeps,
    },
    {
        main: Video, deps: videoDeps,
    },
]);
const gf = new GraphFiller(gd);
gf.fillRecursive(Shop.create(1), Shop);
console.log(gf);
