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
    function addSubtotalReportsSalaryDatatable(){
        let subtotal = {
            'base_salary': 0,
            'allowance': 0,
            'overtime': 0,
            'deduction': 0,
            'thr': 0,
            'bonus': 0,
            'gross_salary': 0,
            'final_salary': 0,
        };

        for (const salary of reports_salary_datatable.rows().data().toArray()) {
            console.log('salary[0]');
            console.log(salary['nik_name']);
            subtotal['base_salary'] += parseInt(salary['base_salary']);
            subtotal['allowance'] += parseInt(salary['allowance']);
            subtotal['overtime'] += parseInt(salary['overtime']);
            subtotal['deduction'] += parseInt(salary['deduction']);
            subtotal['thr'] += parseInt(salary['thr']);
            subtotal['bonus'] += parseInt(salary['bonus']);
            subtotal['gross_salary'] += parseInt(salary['gross_salary']);
            subtotal['final_salary'] += parseInt(salary['final_salary']);
        }

        reports_salary_datatable.row.add({
            nik_name: `<b>TOTAL</b>`,
            department: `<b>-</b>`,
            presence_count: `<b>-</b>`,
            base_salary: `${subtotal['base_salary']}`,
            allowance: `${subtotal['allowance']}`,
            overtime: `${subtotal['overtime']}`,
            deduction: `${subtotal['deduction']}`,
            thr: `${subtotal['thr']}`,
            bonus: `${subtotal['bonus']}`,
            gross_salary: `${subtotal['gross_salary']}`,
            final_salary: `${subtotal['final_salary']}`

        }).draw(true);

    }

	function initReportsSalaryDataTable(fetch_url) {
		$('#reports-salary-table').DataTable().destroy();
		let reports_salary_datatable = $('#reports-salary-table').DataTable({
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
                    data: 'base_salary',
                    defaultContent: '-',
                    render: function(data, type, row){
                        return 'Rp. ' + format_number(data);
                    }
                },
                {
                    data: 'allowance',
                    defaultContent: '-',
                    render: function(data, type, row){
                        return 'Rp. ' + format_number(data);
                    }
                },
                {
                    data: 'overtime',
                    defaultContent: '-',
                    render: function(data, type, row){
                        return 'Rp. ' + format_number(data);
                    }
                },
                {
                    data: 'deduction',
                    defaultContent: '-',
                    render: function(data, type, row){
                        return 'Rp. ' + format_number(data);
                    }
                },
                {
                    data: 'thr',
                    defaultContent: '-',
                    render: function(data, type, row){
                        return 'Rp. ' + format_number(data);
                    }
                },
                {
                    data: 'bonus',
                    defaultContent: '-',
                    render: function(data, type, row){
                        return 'Rp. ' + format_number(data);
                    }
                },
                {
                    data: 'gross_salary',
                    defaultContent: '-',
                    render: function(data, type, row){
                        return 'Rp. ' + format_number(data);
                    }
                },
                {
                    data: 'final_salary',
                    defaultContent: '-',
                    render: function(data, type, row){
                        return 'Rp. ' + format_number(data);
                    }
                },
            ],
            
		});

        return reports_salary_datatable;
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
    let reports_salary_datatable = initReportsSalaryDataTable(fetch_url='fetch-reports-salary/');
    let current_period_filter = null;
    let current_dept_filter = null;

    $('body').on('change','#period-filter, #departments-filter', function(){
        current_period_filter = $('#period-filter').val();
        current_dept_filter = $('#departments-filter').val();
        
        reports_salary_datatable = initReportsSalaryDataTable(fetch_url=`fetch-reports-salary/?pu=${current_period_filter}&du=${current_dept_filter}`);

        $('#report-subtotal-switch').prop('checked', false);

    });

    $('body').on('click','#report-subtotal-switch',function(){
        if ($(this).is(':checked')) addSubtotalReportsSalaryDatatable();
        else reports_salary_datatable.row(':last').remove().draw();
        
    });

	$('#reports-salary-table tfoot th.search-text').each(function () {
		var title = $(this).text();
		$(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
	});
  
});