function unifyImageURL(imgURL) {
    const splitImageUrl = imgURL.split('/');
    let imageUriName = splitImageUrl[splitImageUrl.length - 1];
    // Make it universal (remove size spec)
    const imageUriNameParts = imageUriName.split('.');
    imageUriName = imageUriNameParts.slice(0, -2).join('.') + '.' + imageUriNameParts[imageUriNameParts.length - 1];
    return splitImageUrl.slice(0, -1).join('/') + '/' + imageUriName;
}