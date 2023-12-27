$(function () {
	function initPresencesDataTable() {
		$('#presences-table').DataTable().destroy();
		let presences_datatable = $('#presences-table').DataTable({
            initComplete: function () {
                // Apply the search
                this.api()
                .columns()
                .every(function () {
                    let that = this;

                    $('input', this.footer()).on('keyup change clear', function () {
                        if (that.search() !== this.value) {
                            that.search(this.value).draw();
                        }
                    });
                });
            },
            ajax: {
                url: 'fetch-presences/',
                dataSrc: 'presences_data',
            },
            responsive: true,
            columnDefs: [{ targets: -1, width: '90px' }],
            columns: [
                {
                    data: 'nik_name',
                    defaultContent: '-',
                },
                {
                    data: 'date',
                    defaultContent: '-',
                },
                {
                    data: 'start_at',
                    defaultContent: '-',
                },
                {
                    data: 'end_at',
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
		});

        return presences_datatable;
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

	let presences_datatable =  initPresencesDataTable();
    let overtime_users_datatable = null;

	$('body').on('click', '.delete-presences', function () {
		if (confirm('Do You Want to Deactivate this Presence ?')) {
            let presence_uuid = $(this).data('uq');
            let url = $(this).data('link');
            url = url.replace('@@', presence_uuid);

            $.ajax({
                url: url,
                method: 'POST',
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                },
                success: function (result) {
                    if (result.success === true) {
                        presences_datatable = initPresencesDataTable();
                    } else if (result.success === false) {
                        toastr['error'](result.toast_message);
                    }
                },
                error: function (result) {},
            });
		}
	});

	$('body').on('click','.update-presences, .view-presences, #add-presences', function () {
		let presence_uuid = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', presence_uuid);

		$.ajax({
			url: url,
			method: 'GET',
			success: function (result) {
				if (result.success === true) {
					$('#form-presences-modal .modal-content').html(result.form);
                    
                    if(!result.is_view_only){
                        dselect(document.querySelector('select#employee_id'), {
							search: true,
                            clearable:true,
						});
                    } else {
                        $('#employee_id').addClass('form-control');
                    }

					$('#form-presences-modal').modal('show');
				
				} else if (result.success === false) {
					toastr['error'](result.toast_message);
				}
			},
			error: function (result) {},
		});
	});

	$('body').on('click','#import-presences', function () {
		let presence_uuid = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', presence_uuid);

		$.ajax({
			url: url,
			method: 'GET',
			success: function (result) {
				if (result.success === true) {
					$('#form-presences-modal .modal-content').html(result.form);

					$('#form-presences-modal').modal('show');
				
				} else if (result.success === false) {
					toastr['error'](result.toast_message);
				}
			},
			error: function (result) {},
		});
	});

	$('body').on('click', '#submit-form-presences', function () {
		let form = document.getElementById('presences_form');
		let form_data = new FormData(form);
        
        form_data.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());
        form_data.append('employee_id', $('#employee_id').val());
        
		let presence_uuid = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', presence_uuid);
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

                    presences_datatable = initPresencesDataTable();

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
                
                $('#form-presences-modal').modal(result.is_close_modal === true ? 'hide' : 'show');
            },
            error: function (result) {},
		});
	});

    $('body').on('change','input#start_at, input#end_at',function(){
        let start_at = $('input#start_at').val();
        let end_at = $('input#end_at').val();
        if (start_at !== '' && end_at === '') {
            $('input#end_at').val(start_at);
        } else if (start_at === '' && end_at !== '') {
            $('input#start_at').val(end_at);

        }
        
    });

	$('#presences-table tfoot th.search-text').each(function () {
		let title = $(this).text();
		$(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
	});
  
});
