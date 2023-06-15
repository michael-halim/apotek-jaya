$(function () {
	function initSalariesDataTable() {
		$('#salaries-table').DataTable().destroy();
		let salaries_datatable = $('#salaries-table').DataTable({
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
                url: 'fetch-salaries/',
                dataSrc: 'salaries_data',
            },
            responsive: true,
            columnDefs: [{ targets: -1, width: '90px' }],
            columns: [
                {
                    data: 'name',
                    defaultContent: '-',
                },
                {
                    data: 'description',
                    defaultContent: '-',
                },
                {
                    data: 'value',
                    defaultContent: '-',
                    render: function(data, type, row){
                        return 'Rp. ' + data.toString().replace(/(\d)(?=(\d{3})+$)/g, '$1.');
                    }
                },
                {
                    data: 'created_at',
                    defaultContent: '-',
                },
                {
                    data: 'status',
                        render: function (data, type, row) {
                            if (data === 1) {
                                return '<span class="badge bg-success">Active</span>';
                            } else if (data === 0) {
                                return '<span class="badge bg-danger">Inactive</span>';
                            } else {
                                return '<span class="badge bg-secondary">Unknown</span>';
                            }
                        },
                },
                {
                    data: 'uq',
                },
            ],
            dom: 'lBfrtip',
            buttons: ['copy', 'csv', 'excel', 'pdf', 'print'],
		});

        return salaries_datatable;
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

	let salaries_datatable = initSalariesDataTable();

	// $('body').on('click', '.delete-salaries', function () {
	// 	if (confirm('Do You Want to Deactivate this Salaries ?')) {
    //         let salaries_uuid = $(this).data('uq');
    //         let url = $(this).data('link');
    //         url = url.replace('@@', salaries_uuid);

    //         $.ajax({
    //             url: url,
    //             method: 'POST',
    //             data: {
    //                 csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
    //             },
    //             success: function (result) {
    //                 if (result.success === true) {
    //                     benefit_datatable = initSalariesDataTable();
    //                 } else if (result.success === false) {
    //                     toastr['error'](result.toast_message);
    //                 }
    //             },
    //             error: function (result) {},
    //         });
	// 	}
	// });

	$('body').on('click','.update-salaries, .view-salaries, #add-salaries', function () {
		let salary_uuid = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', salary_uuid);

		$.ajax({
			url: url,
			method: 'GET',
			success: function (result) {
				if (result.success === true) {
                    console.log(result);
					$('#form-salaries-modal .modal-content').html(result.form);

                    let value = $('input#value').val();
                    value = value.replace(/(\d)(?=(\d{3})+$)/g, '$1.');
                    $('input#value').val(value);

					$('#form-salaries-modal').modal('show');
				
				} else if (result.success === false) {
					toastr['error'](result.toast_message);
				}
			},
			error: function (result) {},
		});
	});

	$('body').on('click', '#submit-form-salaries', function () {
		let form = document.getElementById('salaries_form');
		let form_data = new FormData(form);
        let cleaned_value = $('input#value').val().replace(/\D/g, '');

        form_data.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());
        form_data.delete('value');
        form_data.append('value', cleaned_value);

		let salary_uuid = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', salary_uuid);

		$.ajax({
            url: url,
            method: 'POST',
            processData: false,
            contentType: false,
            data: form_data,
            success: function (result) {
                $('.form-error').html('');
                $('.is-invalid').removeClass('is-invalid');

                if (result.success === true) {
                    $('.modal-messages').css({ display: 'none' }).html('');
                    toastr['success'](result.toast_message);

                    benefit_datatable = initSalariesDataTable();

                } else if (result.success === false) {
                    for (const keys in result.errors) {
                        $('#' + keys).addClass('is-invalid');

                        let error_list = '';
                        for (const err of result.errors[keys]) {
                            error_list += err + '<br>';
                        }
                        
                        $('#' + keys).next('.form-error').html(error_list);
                    }

                    let messages_element = '';
                    for (const message of result.modal_messages) {
                        messages_element += `<li class= "${message.tags}">${message.message}</li>`;
                    }

                    $('.modal-messages').css({ display: 'block' }).html(messages_element);

                    toastr['error'](result.toast_message);
                }
                
                $('#form-salaries-modal').modal(result.is_close_modal === true ? 'hide' : 'show');
            },
            error: function (result) {},
		});
	});

    $('body').on('keyup','input#value',function(){
        let current_value = $(this).val().replace(/\D/g, '');

        // Add a '.' after every 3 digits from the end of the input
        current_value = current_value.replace(/(\d)(?=(\d{3})+$)/g, '$1.');

        $(this).val(current_value);
    
    });

	$('#salaries-table tfoot th.search-text').each(function () {
		var title = $(this).text();
		$(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
	});
  
});
