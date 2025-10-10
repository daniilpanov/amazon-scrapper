function checkNumber(positiveNumberStr, def = null) {
    if (!positiveNumberStr || positiveNumberStr[0] === '-')
        return def;
    return Number.parseFloat(positiveNumberStr);
}

function mapProductData(original, domain) {
    return {
        product_id: original.asin,
        domain,
        product_title: original.title || '',
        main_image_url: original.imageUrl || null,
        price: original.price ? original.price / 100 : null,
        rating: checkNumber(original.reviewsRating, 0),
        age: original.ageInMonths || null,
        number_of_images: original.numberOfImages || 0,
        variation_count: original.variationCount || 0,
        weight: checkNumber(original.weight),

        product_identifiers: {
            ...(original.upc && { UPC: original.upc }),
            ...(original.ean && { EAN: original.ean }),
            ...(original.gtin && { GTIN: original.gtin }),
            ...(original.isbn && { ISBN: original.isbn }),
        },
        shipping_details: {
            height: checkNumber(original.height),
            width: checkNumber(original.width),
            length: checkNumber(original.length),
        },

        category: original.categoryTitle || null,
        category_url: original.bestSellersUrl || null,
        rank: original.salesRank || null,

        subcategory: original.subcategories?.[0]?.nodeName || null,
        subcategory_rank: original.subcategories?.[0]?.subcategoryBsr || null,
        subcategory_url: original.subcategories?.[0]?.subcategoryUrl || null,

        parent_level_sales: original.monthlySales || null,
        asin_sales: original.childMonthlySales || null,
        parent_level_revenue: original.monthlyRevenue ? original.monthlyRevenue / 100 : null,
        asin_revenue: original.childMonthlyRevenue ? original.childMonthlyRevenue / 100 : null,
        parent_level_change: original.salesChange || null,
        asin_change: original.childSalesChange || null,

        storage_fee: original.storageFee || null,
        last_year_sales: original.yearSales || null,
        best_sales_period: original.bestMonth ? `${original.bestMonth}-01` : null,
        sales_to_reviews: original.salesToReviews ? parseFloat(original.salesToReviews) : null,

        brand: original.brand || null,
        seller: original.bbSeller || null,
        seller_region: original.bbSellerCountry !== 'N/A' ? (original.bbSellerCountry || null) : null,
    };
}

function categoriesToObject(original) {
    let res = {};
    for (const item of original)
        res = { ...res, ...item };
    return res;
}
