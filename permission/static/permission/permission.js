$(function () {
    function initDataTable(){
        $('#permission-table').DataTable().destroy();
        $('#permission-table').DataTable({
            initComplete: function () {
                // Apply the search
                this.api()
                    .columns()
                    .every(function () {
                        var that = this;

                        $('input', this.footer()).on('keyup change clear', function () {
                            if (that.search() !== this.value) {
                                that.search(this.value).draw();
                            }
                        });
                    });
            },

            ajax: {
                url: 'list-permission/',
                dataSrc: 'permission_data',
            },
            responsive: true,
            columnDefs: [
            ],
            columns: [
                {
                    data: 'nik',
                    defaultContent: '-',
                },
                {
                    data: 'name',
                    defaultContent: '-',
                },
                {
                    data: 'department',
                    defaultContent: '-',
                },
                {
                    data: 'group_name',
                    defaultContent: '-',
                },
                {
                    data: 'permission',
                    defaultContent: '-',
                },
                {
                    data: 'uq',
                    defaultContent: '-',
                },
            ],
            dom: 'lBfrtip',
            buttons: ['copy', 'csv', 'excel', 'pdf', 'print'],

        });
    }
    
    toastr.options = {
        closeButton: false,
        debug: false,
        newestOnTop: false,
        progressBar: true,
        positionClass: 'toast-top-right',
        preventDuplicates: false,
        onclick: null,
        showDuration: '300',
        hideDuration: '1000',
        timeOut: '5000',
        extendedTimeOut: '1000',
        showEasing: 'swing',
        hideEasing: 'linear',
        showMethod: 'fadeIn',
        hideMethod: 'fadeOut',
    };

    initDataTable();

    $('#permission-table tfoot th.search-text').each(function () {
        var title = $(this).text();
        $(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
    });

});