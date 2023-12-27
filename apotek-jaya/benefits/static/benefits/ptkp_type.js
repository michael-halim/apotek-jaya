$(function () {
    function format_number(num) {
        // Add a '.' after every 3 digits from the end of the input
        num = num.toString().replace(/\D/g, '');
        num = num.toString().replace(/^(0{1,})(\d+)/g, '$2');
        num = num.replace(/(\d)(?=(\d{3})+$)/g, '$1.')
        if (num == '') num = '0';
            
        return num
    }

	function initPTKPTypesDataTable() {
		$('#ptkp-type-table').DataTable().destroy();
		let ptkp_type_datatable = $('#ptkp-type-table').DataTable({
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
                url: 'ptkp/fetch-ptkp-type/',
                dataSrc: 'ptkp_type_data',
            },
            responsive: true,
            columnDefs: [
                { targets: -1, width: '90px' },
                { targets: 1, type:'currency' },
            ],
            columns: [
                {
                    data: 'name',
                    defaultContent: '-',
                    render: function(data, type, row){
                        return data.toUpperCase();
                    }
                },
                {
                    data: 'value',
                    defaultContent: '-',
                    render: function(data, type, row){
                        return 'Rp. ' + format_number(data);
                    }
                },
                {
                    data: 'uq',
                },
            ],
            // Custom sorting plug-in for currency values
            oSort: {
                'currency-pre': function (a) {
                    return a.replace(/\D/g, '');
                },
                'currency-asc': function (a, b) {
                    return a - b;
                },
                'currency-desc': function (a, b) {
                    return b - a;
                },
            },
		});

        return ptkp_type_datatable;
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

	let ptkp_type_datatable =  initPTKPTypesDataTable();
	
    $('body').on('click', '.delete-ptkp-type', function () {
		if (confirm('Do You Want to Delete this PTKP Type For Good ?')) {
            let ptkp_type_uuid = $(this).data('uq');
            let url = $(this).data('link');
            url = url.replace('@@', ptkp_type_uuid);

            $.ajax({
                url: url,
                method: 'POST',
                data: {
                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                },
                success: function (result) {
                    if (result.success === true) {
                        ptkp_type_datatable = initPTKPTypesDataTable();
                    } else if (result.success === false) {
                        toastr['error'](result.toast_message);
                    }
                },
                error: function (result) {},
            });
		}
	});

	$('body').on('click','.update-ptkp-type, .view-ptkp-type, #add-ptkp-type', function () {
		let ptkp_type_uuid = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', ptkp_type_uuid);

		$.ajax({
			url: url,
			method: 'GET',
			success: function (result) {
				if (result.success === true) {
					$('#form-ptkp-type-modal .modal-content').html(result.form);

                    $('input#value').val('Rp. ' + format_number($('input#value').val()));

                    $('#form-ptkp-type-modal').modal('show');
				
				} else if (result.success === false) {
					toastr['error'](result.toast_message);
				}
			},
			error: function (result) {},
		});
	});

    $('body').on('click','#import-ptkp-type', function () {
		let ptkp_type_id = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', ptkp_type_id);
        alert(url);
        $.ajax({
			url: url,
			method: 'GET',
			success: function (result) {
				if (result.success === true) {
					$('#form-ptkp-type-modal .modal-content').html(result.form);

					$('#form-ptkp-type-modal').modal('show');
				
				} else if (result.success === false) {
					toastr['error'](result.toast_message);
				}
			},
			error: function (result) {},
		});
	});

	$('body').on('click', '#submit-form-ptkp-type', function () {
        let form = document.getElementById('ptkp_type_form');
		let form_data = new FormData(form);
        
        form_data.append('csrfmiddlewaretoken', $('input[name=csrfmiddlewaretoken]').val());
        if ($('input#value').val() !== undefined) {
            form_data.delete('value');
            form_data.append('value', $('input#value').val().replace(/\D/g, ''));
        }

		let ptkp_type_uuid = $(this).data('uq');
		let url = $(this).data('link');
		url = url.replace('@@', ptkp_type_uuid);
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

                    ptkp_type_datatable = initPTKPTypesDataTable();

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
                
                $('#form-ptkp-type-modal').modal(result.is_close_modal === true ? 'hide' : 'show');
            },
            error: function (result) {},
		});
	});
    
    $('body').on('keyup','input#value',function(){
        let current_value = $(this).val();
        $(this).val('Rp. ' + format_number(current_value));
    
    });

	$('#ptkp-type-table tfoot th.search-text').each(function () {
		var title = $(this).text();
		$(this).html('<input class="form-control" type="text" placeholder="Search ' + title + '" />');
	});
  
});