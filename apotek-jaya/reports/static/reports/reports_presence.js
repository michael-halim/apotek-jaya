$(function () {
    function format_number(num) {
        // Add a '.' after every 3 digits from the end of the input
        num = num.toString().replace(/\D/g, '');
        num = num.toString().replace(/^(0{1,})(\d+)/g, '$2');
        num = num.replace(/(\d)(?=(\d{3})+$)/g, '$1.')
        if (num == '') num = '0';
            
        return num
    }

    function fetch_salary_filter(){
        $.ajax({
            url : 'fetch-period/', 
            method : 'GET', 
            success:function(result){
                let option = '<option value="---------">---------</option>';
                if (result['success']){
                    for (data of result['payroll_periods_data']){
                        option += `<option value="${data['hash']}">${data['name']} (${data['start_at']} - ${data['end_at']})</option>`;
                    }
                }
                $('#period-filter').html(option);
            },
            error:function(result){}
        });
    }

    function fetch_departments_filter(){
        $.ajax({
            url : 'fetch-departments/', 
            method : 'GET', 
            success:function(result){
                let option = '<option value="---------">---------</option>';
                if (result['success']){
                    for (data of result['departments_data']){
                        option += `<option value="${data['hash']}">${data['name']}</option>`;
                    }
                }
                $('#departments-filter').html(option);
            },
            error:function(result){}
        });
    }
    
    function addSubtotalReportsPresenceDatatable(){
        let subtotal = {
            'presence_count': 0,
            'total_work_hours': 0,
            'overtime_hours_count': 0,
            'leave_count': 0,
            'sick_count': 0,
            'permit_count': 0,
        };

        for (const salary of reports_presence_datatable.rows().data().toArray()) {
            subtotal['presence_count'] += parseInt(salary['presence_count']);
            subtotal['total_work_hours'] += parseInt(salary['total_work_hours']);
            subtotal['overtime_hours_count'] += parseInt(salary['overtime_hours_count']);
            subtotal['leave_count'] += parseInt(salary['leave_count']);
            subtotal['sick_count'] += parseInt(salary['sick_count']);
            subtotal['permit_count'] += parseInt(salary['permit_count']);
        }

        reports_presence_datatable.row.add({
            nik_name: `<b>TOTAL</b>`,
            department: `<b>-</b>`,
            presence_count: `${subtotal['presence_count']}`,
            total_work_hours: `${subtotal['total_work_hours']}`,
            overtime_hours_count: `${subtotal['overtime_hours_count']}`,
            leave_count: `${subtotal['leave_count']}`,
            sick_count: `${subtotal['sick_count']}`,
            permit_count: `${subtotal['permit_count']}`,

        }).draw(true);

    }

	function initReportsPresenceDataTable(fetch_url) {
		$('#reports-presence-table').DataTable().destroy();
		let reports_presence_datatable = $('#reports-presence-table').DataTable({
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
                url: fetch_url,
                dataSrc: 'reports_salary_data',
            },
            responsive: true,
            columns: [
                {
                    data: 'nik_name',
                    defaultContent: '-',
                },
                {
                    data: 'department',
                    defaultContent: '-',
                },
                {
                    data: 'presence_count',
                    defaultContent: '-',
                },
                {
                    data: 'total_work_hours',
                    defaultContent: '-',
                },
                {
                    data: 'overtime_hours_count',
                    defaultContent: '-',
                },
                {
                    data: 'leave_count',
                    defaultContent: '-',
                },
                {
                    data: 'sick_count',
                    defaultContent: '-',
                },
                {
                    data: 'permit_count',
                    defaultContent: '-',
                },
            ],
            
		});

        return reports_presence_datatable;
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

    let reports_period_filter = fetch_salary_filter();
    let reports_departments_filter = fetch_departments_filter();
    let reports_presence_datatable = initReportsPresenceDataTable(fetch_url='fetch-reports-presence/');
    let current_period_filter = null;
    let current_dept_filter = null;

    $('body').on('change','#period-filter, #departments-filter', function(){
        current_period_filter = $('#period-filter').val();
        current_dept_filter = $('#departments-filter').val();
        
        reports_presence_datatable = initReportsPresenceDataTable(fetch_url=`fetch-reports-presence/?pu=${current_period_filter}&du=${current_dept_filter}`);

        $('#report-subtotal-switch').prop('checked', false);

    });

    $('body').on('click','#report-subtotal-switch',function(){
        if ($(this).is(':checked')) addSubtotalReportsPresenceDatatable();
        else reports_presence_datatable.row(':last').remove().draw();
        
    });

	$('#reports-presence-table tfoot th.search-text').each(function () {
		var title = $(this).text();
		$(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
	});
  
});