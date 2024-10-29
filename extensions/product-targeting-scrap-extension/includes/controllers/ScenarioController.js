import { Scenario } from '../models/Scenario';

export class ScenarioController {
    dependencies = {
        bsr: ['parser', 'multiparser', 'bsr'],
        search: ['parser', 'multiparser', 'search'],
        product: ['parser', 'product'],
        reviews: ['parser', 'multiparser', 'reviews'],
        helium: ['parser', 'helium'],
        heliumLogin: ['parser', 'heliumlogin'],
    };

    async buildBSR(url) {
        const scenario = new Scenario(this.dependencies.bsr);
        await scenario.createTab(url);
        let result;
        do {
            await scenario.loadDependencies();
            scenario.appendFunction(async () => {
                const bsrParser = new BSRMultiParser();
                await bsrParser.waitLoading();
                return { asins: bsrParser.findASINsList(), nextPage: bsrParser.clickNextPage() };
            });

            result = await scenario.applyFunctionsSync();
            await new Promise(r => setTimeout(500, r));
        } while (result.nextPage);
        return result;
    }

    async buildSearch(search) {
        const scenario = new Scenario(this.dependencies.search);
        await scenario.createTab('https://www.amazon.com/s?k=' + search.replaceAll(' ', '+').replaceAll(',', '%2C'));
        let result;
        do {
            await scenario.loadDependencies();
            scenario.appendFunction(async () => {
                const searchParser = new SearchMultiParser();
                await searchParser.waitLoading();
                searchParser.findElements();
                searchParser.appendFunctions([
                    searchParser.getASIN, searchParser.getTitle,
                    searchParser.getPrice, searchParser.getImageLinks,
                    searchParser.getReviewsCount, searchParser.getReviewsRating,
                ]);
                return searchParser.applyFunctions();
            });

            result = await scenario.applyFunctionsSync();
            await new Promise(r => setTimeout(500, r));
        } while (result.nextPage);
        return result;
    }

    async buildProduct(ASIN) {
        const scenario = new Scenario(this.dependencies.product);
        await scenario.createTab('https://www.amazon.com/dp/' + ASIN + '?th=1');
        await scenario.loadDependencies();
        scenario.appendFunction(async () => {
            const productParser = new ProductsParser();
            await productParser.waitLoading();
            productParser.appendFunctions([
                productParser.getBreadcrumbs, productParser.getCurrentBreadcrumb,
                productParser.getASIN, productParser.getMarketplaceId,
                productParser.getTitle, productParser.getDescription,
                productParser.getReviewsCount, productParser.getReviewsRating,
                productParser.getPrice, productParser.getTechnicalDetails,
                productParser.getOptions, productParser.getFullMediaConfig,
                productParser.getRelatedVideos, productParser.getAspects,
                productParser.getAdditionalInfo, productParser.getDetails,
            ]);
            return productParser.applyAsyncFunctions();
        });

        return await scenario.applyFunctionsSync();
    }

    async buildReviews(ASIN, tabId?) {
        // Goto the product card if no tabId given
        if (!tabId) {
            const productScenario = new Scenario(this.dependencies.product);
            await productScenario.createTab('https://www.amazon.com/dp/' + ASIN + '?th=1');
            await productScenario.loadDependencies();
            productScenario.appendFunction(async () => {
                const productParser = new ProductsParser();
                await productParser.waitLoading();
                return productParser.clickAllReviews();
            });
            await productScenario.applyFunctionsSync();
            await new Promise(r => setTimeout(500, r));
            tabId = productScenario.tabId
        }
        const reviewsScenario = new Scenario(this.dependencies.reviews);
        reviewsScenario.tabId = tabId;
        let result;
        do {
            await reviewsScenario.loadDependencies();
            reviewsScenario.appendFunction(async () => {
                const reviewsParser = new ReviewsMultiParser();
                await reviewsParser.waitLoading();
                reviewsParser.findElements();
                reviewsParser.appendFunctions([
                    reviewsParser.getReviewId, reviewsParser.getTitle,
                    reviewsParser.getContent, reviewsParser.getNickname,
                    reviewsParser.getRating, reviewsParser.getDateAndPlace,
                    reviewsParser.getOptions, reviewsParser.getHelpful,
                ]);
                return reviewsParser.applyFunctions();
            });

            result = await reviewsScenario.applyFunctionsSync();
            await new Promise(r => setTimeout(500, r));
        } while (result.nextPage);
        await reviewsScenario.loadDependencies();
        reviewsScenario.appendFunction(async () => {
            const reviewsParser = new ReviewsMultiParser();
            reviewsParser.appendFunctions([

            ]);
            return reviewsParser.clickNextPage();
        });

        return await reviewsScenario.applyFunctionsSync();
    }


    // TODO: helium build
    async buildHelium() {

    }

    async buildHeliumLogin() {

    }
}