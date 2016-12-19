<html>
<style>
table {
    border-collapse: collapse;
    width:100%
}

table, td, th {
    border: 1px solid black;
}
.title-format{
    text-align: center
    }
.number-fomat{
    text-align: right;
    margin-right: 2px;
    }
.dontsplit {page-break-before: always;}
.list {
  	page-break-inside: avoid;
  	}
</style>
% for o in objects:
    <body >
        <div class="dontsplit">
            <% variable1 = 2 %>
            <% variable2 = variable1 + 12 %>
            <p >Name : ${ o.name }</p>
            <p >Date : ${ o.date_order }</p>
            <table>
                <thead>
                    <tr align="left">
                        <th class="title-format ">Sequence</th>
                        <th class="title-format">Job</th>
                        <th class="title-format">Code</th>
                        <th class="title-format">Description</th>
                        <th class="title-format">Brand</th>
                        <th class="title-format">Plan Qty</th>
                        <th class="title-format">Qty.</th>
                        <th class="title-format">Unit</th>
                        <th class="title-format">Unit Price</th>
                        <th class="title-format">Offered</th>
                        <th class="title-format">Final</th>
                    </tr>
                </thead>
                <% var = 0%>
                % for line in sorted(o.order_line, key = lambda x: (x.sequence, o.order_line), reverse = True):
                    <div class="list">
                        <% var += float(line.final_subtotal)%>
                    </div>
                    <tbody>
                        <tr>
                            <td class="title-format">${line.sequence}</td>
                            <td >${line.account_analytic_id.code} - ${line.account_analytic_id.name}</td>
                            <td class="title-format">${line.product_id.code}</td>
                            <td>${line.name}</td>
                            <td>brand</td>
                            <td class="title-format">${line.plan_qty}</td>
                            <td class="title-format">${line.product_qty}</td>
                            <td class="title-format">${line.product_uom.id}</td>
                            <td class="number-fomat">${line.price_unit}</td>
                            <td class="number-fomat">${line.price_subtotal}</td>
                            <td class="number-fomat">${"{0:,.2f}".format(line.final_subtotal)}</td>
                        </tr>
                    </tbody>
                % endfor
                <tfoot>
                    <tr>
                        <td align="center" colspan="10" >${ variable2 }</td>
                        <td>${ "{0:,.2f}".format(var) }</td>
                    </tr>
                </tfoot>
            </table>
        </div>
    </body>
% endfor
</html>