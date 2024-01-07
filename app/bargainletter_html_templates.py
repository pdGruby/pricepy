main_message_html = """
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Potencjalne Oferty Inwestycyjne</title>
</head>
<body>
    <p>Cześć!</p>
    <p>Znaleźliśmy potencjalne oferty inwestycyjne, które spełniają Twoje oczekiwania. Poniżej więcej szczegółów.</p>

    <table style="width: 100%; border-collapse: collapse; margin: 0 auto;">
        <thead>
            <tr>
                <th style="border: 1px solid #000; width: 18%; text-align: center;"><strong>Potencjalny zwrot [%]</strong></th>
                <th style="border: 1px solid #000; width: 18%; text-align: center;"><strong>Rzeczywista cena [zł]</strong></th>
                <th style="border: 1px solid #000; width: 18%; text-align: center;"><strong>Przewidywana cena [zł]</strong></th>
                <th style="border: 1px solid #000; width: 18%; text-align: center;"><strong>Rzeczywista cena za m<sup>2</sup> [zł/m<sup>2</sup>]</strong></th>
                <th style="border: 1px solid #000; width: 18%; text-align: center;"><strong>Przewidywana cena za m<sup>2</sup> [zł/m<sup>2</sup>]</strong></th>
                <th style="width: 10%; text-align: center; border-left: none; border-top: none"></th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    
    <br>
    <strong>Ustawione filtry:</strong>
    <br>Maksymalna cena rzeczywista -> {max_real_price} zł
    <br>Minimalny zwrot z inwestycji -> {min_potential_gain}%
    <br>Lokalizacja -> {location}

    <p>Życzymy wysokich zwrotów z inwestycji :)</p>
    <p><img src="https://zapodaj.net/images/99a9135270eaa.png" alt="pricepy" width="465" height="129"></p>
</body>
</html>
"""


table_row_html = """
<tr>
    <td style="border: 1px solid #000; text-align: center; color: #29de18"><strong>{potential_gain}</strong></td>
    <td style="border: 1px solid #000; text-align: center;">{real_price}</td>
    <td style="border: 1px solid #000; text-align: center;">{predicted_price}</td>
    <td style="border: 1px solid #000; text-align: center;">{real_price_per_square}</td>
    <td style="border: 1px solid #000; text-align: center;">{predicted_price_per_square}</td>
    <td style="border: 1px solid #000; text-align: center; color: #10500a;"><strong><a style="color: #339966;" href="{link}">LINK</a></strong></td>
</tr>
"""