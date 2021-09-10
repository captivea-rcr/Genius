from odoo import api, fields, models
import datetime
from datetime import time

class SaleOrder(models.Model):
    
    _inherit = "sale.order"
    
    
    @api.model
    def getOrderAmount(self, interval = 0):
        now = datetime.datetime.now()
        today = now.date()
        interval = 1
        startTime = datetime.datetime.combine(fields.Date.from_string(today), time.min)
        endTime = datetime.datetime.combine(fields.Date.from_string(today), time.max)
        crntTime = now - datetime.timedelta(minutes = interval)
        befrTime = crntTime - datetime.timedelta(hours = 3)
        domainSTm = crntTime.strftime("%Y-%m-%d %H:%M")
        domainETm = befrTime.strftime("%Y-%m-%d %H:%M")
        self._cr.execute("""select k.date_part as x , k.y
                            from
                            (select distinct EXTRACT(EPOCH FROM q.min_interval AT TIME ZONE 'UTC') ,sum(q.total) as y
                                from
                                (select DISTINCT p.min as min_interval ,p.hm as hr_min,
                                    CASE
                                      WHEN (p.hm = n.hour_min) THEN n.total
                                      ELSE 0
                                     END AS total
                                from
                                    (select  m.minute as min,to_char(m.minute, 'hh24:mi') as hm
                                        from
                                        (select DISTINCT generate_series(timestamp %s, timestamp %s, interval  '1 min') as minute
                                        from sale_order order by 1) m 
                                     )p,
                                    (select to_char(confirmation_date, 'hh24:mi') as hour_min,sum(amount_total) as total
                                    from sale_order where state = 'sale' and confirmation_date >= now()::date + interval '1h'
                                    group by hour_min
				    union
				    select '00:00' as hour_min,0.0 as total) n)q
                            where q.min_interval >= %s
                            AND    q.min_interval <  %s
                            group by q.min_interval)k
                            order by 1""", (startTime,endTime,domainETm,domainSTm,))
        saleOrder = self._cr.dictfetchall()
        return saleOrder
    
