update products set framing='Withou' where framing in ('Withou ', ' ()')

update products set framing='Withou' where framing in ('Withou ', ' ()')
update products set finishing='Artshots' where finishing='ARTSHOTS'
update products set framing='Alubond' where framing ='Alubond '

update products set finishing=initcap(finishing)

select distinct(concat(category, ' - ' , finishing, ' - ', framing)) as atributos from price_audit