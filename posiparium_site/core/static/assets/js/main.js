    function is_touch_device() {
        return 'ontouchstart' in window
            || navigator.maxTouchPoints;
    }

    function getURLParameters() {
        var url = window.location.href,
            result = [],
            searchIndex = url.indexOf("?");

        if (searchIndex == -1 ) return result;

        var sPageURL = url.substring(searchIndex +1),
            sURLVariables = sPageURL.split('&');
        for (var i = 0; i < sURLVariables.length; i++) {
            result[i] = decodeURIComponent(sURLVariables[i].replace(/\+/g, '%20'));
        }
        return result;
    }

    function populateUaMap() {
        console.log('run map');

        var $container = $('#ua-map .svg-image'),
            json = $container.data('json'),
            $svgPaths = $container.find('svg path');

        $.getJSON( json, {format: "json"})
            .done(function( data ) {

                $svgPaths.each(function( index ) {
                    var $this = $(this),
                        id = $this.attr('id'),
                        skip = $this.data('skip');

                    for(var i=0; i< data.length; i++) {
                        if (id == data[i].slug && skip !== 1) {
                            $this.attr('data-oblast', data[i].name ).attr('data-pep', data[i].num_mps ).attr('data-posipak', data[i].num_minions ).attr('data-url', data[i].url );
                            $this.addClass('popover-dismiss').css('cursor', 'pointer');
                        }
                    }

                    if (skip !== 1) {
                        $('.popover-dismiss').popover({
                            trigger: 'manual',
                            html: true,
                            placement: 'top',
                            container: 'body',
                            animation: false,
                            title: function() {
                                var popoverHTML = $(this).data('oblast');
                                return popoverHTML;
                            },
                            content: function() {
                                var popoverHTML = '<a href="' + $(this).data('url') + '">' +
                                    '<p>Депутатів: ' +  $(this).data('pep') + '</p>'
                                    +  '<p>Помічників: ' +  $(this).data('posipak')  + '</p>'
                                    + '</a>' ;

                                return popoverHTML;
                            }
                        }).on("mouseenter", function () {
                            var _this = this;
                            $(this).popover("show");
                            $(".popover").on("mouseleave", function () {
                                $(_this).popover('hide');
                            });
                        }).on("mouseleave", function () {
                            var _this = this;
                            setTimeout(function () {
                                if (!$(".popover:hover").length) {
                                    $(_this).popover("hide");
                                }
                            }, 1000);
                        });
                    }

                });

                for(var i=0; i<data.length; i++) {
                    data[i].name = '<a href="' + data[i].url + '">' + data[i].name + '</a>';
                }

                $('#ua-map-table').dataTable({
                    "responsive": true,
                    "autoWidth": true,
                    "paging": false,
                    "searching": false,
                    "info": false,
                    "filter": false,
                    "language": {
                        "sProcessing":   "Зачекайте...",
                        "sLengthMenu":   "Показати _MENU_ записів",
                        "sZeroRecords":  "Записи відсутні.",
                        "sInfo":         "Записи з _START_ по _END_ із _TOTAL_ записів",
                        "sInfoEmpty":    "Записи з 0 по 0 із 0 записів",
                        "sInfoFiltered": "(відфільтровано з _MAX_ записів)",
                        "sInfoPostFix":  "",
                        "sSearch":       "Пошук:",
                        "sUrl":          "",
                        "oPaginate": {
                            "sFirst": "Перша",
                            "sPrevious": "Попередня",
                            "sNext": "Наступна",
                            "sLast": "Остання"
                        },
                        "oAria": {
                            "sSortAscending":  ": активувати для сортування стовпців за зростанням",
                            "sSortDescending": ": активувати для сортування стовпців за спаданням"
                        }
                    },
                    "pageLength": 5,
                    "pagingType": "simple",
                    "aaData": data,
                    "aoColumns": [{
                        "mDataProp": "name",
                        "sTitle":"Область"
                    }, {
                        "mDataProp": "num_mps",
                        "sTitle":"Депутатів"
                    }, {
                        "mDataProp": "num_minions",
                        "sTitle":"Помічників"
                    }]
                });

                $('#ua-map svg path[data-oblast][data-oblast!=""]').on({
                    mouseenter: function () {
                        $(this).attr('fill', '#f5b351');
                    },
                    mouseleave: function () {
                        $(this).attr('fill', '#ffffff');
                    }
                });
            });
    }

    function updateSearchForm() {
        var urlParams = getURLParameters();

        for (var i = 0; i < urlParams.length; i++) {
            var sParameter = urlParams[i].split('='),
                sValue = sParameter[1],
                sName = sParameter[0];

            if (sValue.length > 0 && sName === 'q') {
                if(sValue.length > 50)  {
                    sValue = sValue.substring(0,50) + '...'
                }
                $('.search-string').html(': ' + sValue);
            }
        }
    }

    $(document).on('show.bs.popover', function() {
        $('.popover').not(this).popover('hide');
    });

    function wrapPosipakyList() {
        var $container = $('.small-profile .posipaky');

        $container.each(function( index ) {
            var $this = $(this),
                $item = $this.find('.link_nb');

            if($item.length > 5) {
                $this.find('.link_nb:nth-child(6)').after("<span class='show-more'>Показати всіх (" + $item.length + ")</span>").nextAll().addClass('hidden');
            }
        });

        $(document).on('click', '.show-more', function(e){
            e.preventDefault();
            $(e.target).parents('.small-profile').addClass('open');
            $('body').addClass('open');
        });

        $(document).click(function(event) {
            if(!$(event.target).closest('.small-profile').length) {
                $('.small-profile').removeClass('open');
                $('body').removeClass('open');
            }

            if(!$(event.target).closest('.float-search').length && $('body.open-search').length) {
                $('body').removeClass('open-search');
            }
        });
    }

    $('.searchbox button').click(function() {
        $('.searchbox form').submit();
    });

    $(document).ready(function() {
        if ($('.map').length > 0) {
            populateUaMap();
        }

        if (is_touch_device()) {
            $('html').addClass('is-touch');
        }

        updateSearchForm();
        wrapPosipakyList();

        $(".search-name").typeahead({
            minLength: 2,
            autoSelect: false,
            source: function(query, process) {
                $.get('/ajax/suggest', {"q": query})
                    .done(function(data){
                        process(data);
                    })
            },
            matcher: function() {
                return true;
            }
        });

        $('.search-name').on('keydown', function(e) {
            if (e.keyCode == 13) {
                var ta = $(this).data('typeahead'),
                    val = ta.$menu.find('.active').data('value');
                if (val)
                    $(this).val(val);
                $(this.form).submit();
            }
        });
    });