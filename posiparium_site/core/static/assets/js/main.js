document.addEventListener(
    "touchstart",
    function(){},
    true
);


    //two-way-binding 'dropdown as select' and intput field
    //eg.: <ul class="dropdown-as-select" data-linked-input="someID">
    //     <li><a href="#" data-value="value">value</a></li>
    //..
    //<input id="someID" class="linked-input" value="value" />
    $(".dropdown-as-select li a").click(function(){
        var $dropdown = $(this).parents(".dropdown"),
            $dropdownButton = $dropdown.find('.btn'),
            $linkedInput = $('#' + $(this).parents(".dropdown-as-select").data('linked-input'));

        $dropdownButton.html($(this).text() + ' <span class="caret"></span>');
        $dropdownButton.val($(this).data('value'));
        $linkedInput.val($(this).data('value'));

        $dropdown.find('li').removeClass('selected');
        $(this).parent('li').addClass('selected');
    });

    function setDropdownsValue() {
        var $linkedInputs = $('.linked-input');

        $linkedInputs.each(function( index ) {
            var $this = $(this),
                id = $this.attr('id'),
                value = $this.val(),
                $dropdownAsSelect = $("[data-linked-input='" + id + "']"),
                $link = $dropdownAsSelect.find("[data-value='" + value + "']");

            if ($link.length > 0) {
                $dropdownAsSelect.find('li').removeClass('selected');
                $link.parent('li').addClass('selected');
                $link.click();
            }
        });
    }//end of two-way-binding 'dropdown as select' and intput field

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

    function setExFormStateFromUrl() {
        var urlParams = getURLParameters(),
            usedParams = 0;
        for (var i = 0; i < urlParams.length; i++) {
            var sParameter = urlParams[i].split('='),
                sValue = sParameter[1],
                sName = sParameter[0];

            if(sValue.length > 0) {
                if(sName === 'post_type') {
                    $('input[value="' + sValue + '"]').prop('checked', true);
                    usedParams++;
                }

                if(sName === 'region_type') {
                    $('input[value="' + sValue + '"]').prop('checked', true);
                    usedParams++;
                }

                if(sName === 'region_value') {
                    $('input[name="region_value"]').val(sValue);
                    usedParams++
                }

                if(sName === 'declaration_year')  {
                    $('input[name="declaration_year"]').val(sValue);
                    usedParams++
                }

                if(sName === 'doc_type') {
                    $('input[name="doc_type"]').val(sValue);
                    usedParams++
                }
            }
        }

        if(window.location.hash) {
            var hash = window.location.hash.substring(1); //Puts hash in variable, and removes the # character

            if(hash === 'exsearch') {
                usedParams++;
            }
        }

        if(usedParams > 0) {
            $('#ex-search-form').addClass('ex-search');
            $('#collapseExSearch').addClass('in');
            $(".ex-search-link").attr("aria-expanded","true");
        }

        $(".ex-search-link").click(function(){
            $(this).hide(400);
        });

        $(document).on('click', '#clear-filters', function(){
            $('input[name="region_value"]').val('');
            setDropdownsValue();
            $(":checked").prop('checked', false);
        });

        $(document).on('submit', '#ex-form', function(){
            if (!$('input[name="declaration_year"]').val()) {
                $('input[name="declaration_year"]').remove();
            }

            if (!$('input[name="doc_type"]').val()) {
                $('input[name="doc_type"]').remove();
            }

            if (!$('input[name="region_value"]').val()) {
                $('input[name="region_value"]').remove();
            }
        });
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
                            //trigger: 'hover',
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

    $(document).on('show.bs.popover', function() {
        $('.popover').not(this).popover('hide');
    });

    function wrapPosipakyList() {
        var $container = $('.small-profile .posipaky');

        $container.each(function( index ) {
            var $this = $(this),
                $item = $this.find('.link_nb');

            if($item.length > 3) {
                $this.find('.link_nb:nth-child(4)').after("<a href='#' class='show-more'>Показати всіх (" + $item.length + ")</a>").nextAll().addClass('hidden');
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

    $(document).on('click', '.inner-search-button', function(e){
        e.preventDefault();
        $('body').addClass('open-search');
    });


    $(document).ready(function() {
        if ($('.map').length > 0) {
            populateUaMap();
        }

        setExFormStateFromUrl();
        setDropdownsValue();
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



