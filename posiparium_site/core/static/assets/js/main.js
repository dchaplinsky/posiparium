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
                        id = $this.attr('id');

                    for(var i=0; i< data.length; i++) {
                        if (id == data[i].slug) {
                            $this.attr('data-oblast', data[i].name ).attr('data-pep', data[i].num_mps ).attr('data-posipak', data[i].num_minions ).attr('data-url', data[i].url );
                            $this.addClass('popover-dismiss').css('cursor', 'pointer');
                        }
                    }

                    if($this.data('egg')) {
                        $this.addClass('egg-popover-dismiss').css('cursor', 'pointer');
                    }
                    
                    $('.popover-dismiss').popover({
                        trigger: 'hover',
                        html: true,
                        placement: 'top',
                        container: 'body',
                        animation: false,
                        title: function() {
                            return $(this).data('oblast');
                        },
                        content: function() {
                            var popoverHTML = '<a href="' + $(this).data('url') + '">' +
                                '<p>Депутатів: ' +  $(this).data('pep') + '</p>'
                                +  '<p>Помічників: ' +  $(this).data('posipak')  + '</p>'
                                + '</a>' ;

                            return popoverHTML;
                        }
                    });

                    $('.egg-popover-dismiss').popover({
                        trigger: 'hover',
                        html: true,
                        placement: 'top',
                        container: 'body',
                        animation: false,
                        title: function() {
                            return 'Посіпаки-2:';
                        },
                        content: function() {
                            return $(this).data('egg');
                        }
                    });
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

                var $oblast = $('#ua-map svg path[data-oblast][data-oblast!=""], #ua-map svg path[data-egg][data-egg!=""]');

                $oblast.on({
                    mouseenter: function () {
                        $(this).attr('fill', '#f5b351');
                    },
                    mouseleave: function () {
                        $(this).attr('fill', '#ffffff');
                    }
                });

                $oblast.on('click', function() {
                    var $this = $(this),
                        url = $this.data('url');

                    if(url) {
                        window.location.href = url;
                        window.status = url;
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

        $(".search-form-q").typeahead({
            minLength: 2,
            items: 100,
            autoSelect: false,
            source: function(query, process) {
                $.get($(".search-form-q").data("endpoint"), {
                        "q": query
                    })
                    .done(function(data) {
                        process(data);
                    })
            },
            matcher: function() {
                return true;
            },
            highlighter: function(instance) {
                return instance;
            },
            updater: function(instance) {
                return $(instance).data("sugg_text")
            },
            afterSelect: function(item) {
                var form = $(".search-form-q").closest("form");
                form.find("input[name=is_exact]").val("on");

                form.submit();
            }
        });
    });