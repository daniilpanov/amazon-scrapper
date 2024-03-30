/*!
 * Readmore.js jQuery plugin
 * Author: @jed_foster
 * Project home: jedfoster.github.io/Readmore.js
 * Licensed under the MIT license
 */

(function ($) {

    const readmore = 'readmore',
        defaults = {
            speed: 1000,
            maxHeight: 100,
            heightMargin: 16,
            moreLink: '<a href="#">Read More</a>',
            lessLink: '<a href="#">Close</a>',
            embedCSS: true,
            sectionCSS: 'display: block; width: 100%;',
            startOpen: false,
            expandedClass: 'readmore-js-expanded',
            collapsedClass: 'readmore-js-collapsed',

            // callbacks
            beforeToggle: function () {
            },
            afterToggle: function () {
            }
        };

    function Readmore(element, options) {
        this.element = element;

        this.options = $.extend({}, defaults, options);

        $(this.element).data('max-height', this.options.maxHeight);
        $(this.element).data('height-margin', this.options.heightMargin);

        delete (this.options.maxHeight);

        this._defaults = defaults;
        this._name = readmore;

        this.init();
    }

    Readmore.prototype = {

        init: function () {
            const $this = this;

            $(this.element).each(function () {
                const current = $(this),
                    maxHeight = (current.css('max-height').replace(/[^-\d\.]/g, '') > current.data('max-height')) ? current.css('max-height').replace(/[^-\d\.]/g, '') : current.data('max-height'),
                    heightMargin = current.data('height-margin');

                if (current.css('max-height') != 'none') {
                    current.css('max-height', 'none');
                }

                $this.setBoxHeight(current);

                if (current.outerHeight(true) <= maxHeight + heightMargin) {
                    // The block is shorter than the limit, so there's no need to truncate it.
                    return true;
                } else {
                    current.addClass('readmore-js-section ' + $this.options.collapsedClass).data('collapsedHeight', maxHeight);

                    const useLink = $this.options.startOpen ? $this.options.lessLink : $this.options.moreLink;
                    current.after($(useLink).on('click', function (event) {
                        $this.toggleSlider(this, current, event)
                    }).addClass('readmore-js-toggle'));

                    if (!$this.options.startOpen) {
                        current.css({height: maxHeight});
                    }
                }
            });

            $(window).on('resize', function (event) {
                $this.resizeBoxes();
            });
        },

        toggleSlider: function (trigger, element, event) {
            event.preventDefault();

            const $this = this,
                collapsedHeight = $(element).data('collapsedHeight');

            let newLink, sectionClass, newHeight, expanded = false;
            if ($(element).height() <= collapsedHeight) {
                newHeight = $(element).data('expandedHeight') + 'px';
                newLink = 'lessLink';
                expanded = true;
                sectionClass = $this.options.expandedClass;
            } else {
                newHeight = collapsedHeight;
                newLink = 'moreLink';
                sectionClass = $this.options.collapsedClass;
            }

            // Fire beforeToggle callback
            $this.options.beforeToggle(trigger, element, expanded);

            $(element).animate({'height': newHeight}, {
                duration: $this.options.speed, complete: function () {
                    // Fire afterToggle callback
                    $this.options.afterToggle(trigger, element, expanded);

                    $(trigger).replaceWith($($this.options[newLink]).on('click', function (event) {
                        $this.toggleSlider(this, element, event)
                    }).addClass('readmore-js-toggle'));

                    $(this).removeClass($this.options.collapsedClass + ' ' + $this.options.expandedClass).addClass(sectionClass);
                }
            });
        },

        setBoxHeight: function (element) {
            element.data('expandedHeight', element.outerHeight(true));
        },

        resizeBoxes: function () {
            const $this = this;

            $('.readmore-js-section').each(function () {
                const current = $(this);

                $this.setBoxHeight(current);

                if (current.height() > current.data('expandedHeight') || (current.hasClass($this.options.expandedClass) && current.height() < current.data('expandedHeight'))) {
                    current.css('height', current.data('expandedHeight'));
                }
            });
        },

        destroy: function () {
            const $this = this;

            $(this.element).each(function () {
                const current = $(this);

                current.removeClass('readmore-js-section ' + $this.options.collapsedClass + ' ' + $this.options.expandedClass).css({
                    'max-height': '',
                    'height': 'auto'
                }).next('.readmore-js-toggle').remove();

                current.removeData();
            });
        }
    };

    $.fn[readmore] = function (options) {
        const args = arguments;
        if (options === undefined || typeof options === 'object') {
            return this.each(function () {
                if ($.data(this, 'plugin_' + readmore)) {
                    const instance = $.data(this, 'plugin_' + readmore);
                    instance['destroy'].apply(instance);
                }

                $.data(this, 'plugin_' + readmore, new Readmore(this, options));
            });
        } else if (typeof options === 'string' && options[0] !== '_' && options !== 'init') {
            return this.each(function () {
                const instance = $.data(this, 'plugin_' + readmore);
                if (instance instanceof Readmore && typeof instance[options] === 'function') {
                    instance[options].apply(instance, Array.prototype.slice.call(args, 1));
                }
            });
        }
    }
})(jQuery);