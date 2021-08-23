<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <style type="text/css">
            .overflow_ellipsis {
                text-overflow: ellipsis;
                overflow: hidden;
                white-space: nowrap;
            }
            ${css}
        </style>
    </head>
    <body>
        <%!
        def amount(text):
            return text.replace('-', '&#8209;')  # replace by a non-breaking hyphen (it will not word-wrap between hyphen and numbers)
        %>

        <div class="act_as_table data_table">
            <div class="act_as_row labels">                                          
                <div class="act_as_cell">${_('Dates Filter')}</div>
            </div>
            
            <div class="act_as_row">						
				<div class="act_as_cell">
					%if filter_form(data) == 'filter_date':
						${_('From:')}${formatLang(start_date, date=True) if start_date else u'' }${_('To:')}${ formatLang(stop_date, date=True) if stop_date else u'' }
					%else:
						${_('No Filter')}
					%endif					
				</div>
			</div>
		</div>
		
		<div class="act_as_table list_table">
			<div class="act_as_row">
				<div class="act_as_tbody">	
					<div class="act_as_cell" style="width: 200px;">Name</div>
					<div class="act_as_cell" style="width: 100px;">Slip</div>
					<div class="act_as_cell" style="width: 75px;">Rate</div>
					<div class="act_as_cell" style="width: 50px;">Days</div>
					<div class="act_as_cell" style="width: 100px;">Total</div>
					<div class="act_as_cell" style="width: 100px;">Account Title</div>
					<div class="act_as_cell" style="width: 150px;">Account</div>
					<div class="act_as_cell" style="width: 50px;">Account Owner</div>					
					<div class="act_as_cell" style="width: 50px;">Structure</div>
				</div>				
			</div>	    
        </div>        
        
        %if group_by == 'guards':
        
			%for guard in objects:
				<%
					display_lines = guard.salary_lines
				%>
				<div class="act_as_table list_table" style="margin-top: 10px;">
				<div class="act_as_tbody">	

					<div class="act_as_thead">
						<div class="act_as_row labels">
							<div class="act_as_cell" style="width: 200px;">${guard.name_related}</div>
							<div class="act_as_cell" style="width: 100px;">${guard.guard_contract_id.name}</div>
						</div>
					</div>
				</div>
				</div>

				%if display_lines:
					<div class="act_as_table list_table" style="margin-top: 10px;">
						<div class="act_as_tbody">	
						%for line in display_lines:
							<div class="act_as_row lines">
								<div class="act_as_cell" style="width: 200px;">${line['name']}</div>
								<div class="act_as_cell" style="width: 100px;">${line['number']}</div>
								<div class="act_as_cell" style="width: 75px;">${line['rate']}</div>
								<div class="act_as_cell" style="width: 50px;">${line['quantity']}</div>
								<div class="act_as_cell" style="width: 100px;">${line['total']}</div>
								<div class="act_as_cell" style="width: 100px;">${line['bankacctitle']}</div>
								<div class="act_as_cell" style="width: 150px;">${line['bankacc']}</div>
								<div class="act_as_cell" style="width: 50px;">${line['accowner']}</div>
								
							</div>
						%endfor
						</div>					

					</div>
				%else:					
					<div class="act_as_table list_table">
						<div class="act_as_row lines">
							<div class="act_as_cell" style="width: 200px;">No PaySlip Yet</div>						
						</div>
					</div>


				%endif
			%endfor
		
		%else:
			<%
				net_total = 0	
			%>
			%for post in objects:
				<%
					display_lines = post.salary_lines
					active = post.active
					total = 0	
				%>
				
				%if display_lines or active:
					<div class="act_as_table list_table" style="margin-top: 10px;">
					<div class="act_as_tbody">	

						<div class="act_as_thead">
							<div class="act_as_row labels">
								<div class="act_as_cell" style="width: 200px;">${post.name} (${post.id})</div>
							</div>
						</div>
					</div>
					</div>
			
					%if display_lines:
						<div class="act_as_table list_table" style="margin-top: 10px;">
							<div class="act_as_tbody">	
							%for line in display_lines:
								<div class="act_as_row lines">
									<div class="act_as_cell" style="width: 200px;">${line['name_related']}</div>
									<div class="act_as_cell" style="width: 100px;">${line['number']}</div>
									<div class="act_as_cell" style="width: 75px;">${line['rate']}</div>
									<div class="act_as_cell" style="width: 50px;">${line['quantity']}</div>
									<div class="act_as_cell" style="width: 100px;">${line['total']}</div>
									<div class="act_as_cell" style="width: 100px;">${line['bankacctitle']}</div>
									<div class="act_as_cell" style="width: 150px;">${line['bankacc']}</div>
									<div class="act_as_cell" style="width: 50px;">${line['accowner']}</div>
									<div class="act_as_cell" style="width: 50px;">${line['contract_name']}</div>

								</div>
								<%
									total += line['total'] or 0					
									net_total += line['total'] or 0					
								%>
							%endfor
							</div>

							<div class="act_as_table list_table">
								<div class="act_as_row labels" style="font-weight: bold;">
									<div class="act_as_cell first_column" style="width: 100px;">${post.name}</div>
									<div class="act_as_cell amount" style="width: 75px;">${ formatLang(total) | amount }</div>						
								</div>
							</div>

						</div>
					%else:					
						<div class="act_as_table list_table">
							<div class="act_as_row lines">
								<div class="act_as_cell" style="width: 200px;">No PaySlip Yet</div>						
							</div>
						</div>


					%endif
				%endif
			%endfor
			
			<div class="act_as_table list_table">
				<div class="act_as_row labels" style="font-weight: bold;">
					<div class="act_as_cell first_column" style="width: 100px;">Net Total</div>
					<div class="act_as_cell amount" style="width: 75px;">${ formatLang(net_total) | amount }</div>						
				</div>
			</div>
						
		%endif
        
    </body>
</html>
