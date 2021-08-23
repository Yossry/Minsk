Data is stored in the model `value.log` and its matching table:

.. code-block:: console

    coopaname-test> \d value_log
    +----------------+-----------------------------+---------------------------------------------------------+
    | Column         | Type                        | Modifiers                                               |
    |----------------+-----------------------------+---------------------------------------------------------|
    | id             | integer                     |  not null default nextval('value_log_id_seq'::regclass) |
    | model          | character varying           |  not null                                               |
    | field          | character varying           |  not null                                               |
    | user_id        | integer                     |  not null                                               |
    | date           | date                        |  not null                                               |
    | previous_value | character varying           |                                                         |
    | new_value      | character varying           |                                                         |
    | create_uid     | integer                     |                                                         |
    | create_date    | timestamp without time zone |                                                         |
    | write_uid      | integer                     |                                                         |
    | record_id      | integer                     |                                                         |
    | write_date     | timestamp without time zone |                                                         |
    +----------------+-----------------------------+---------------------------------------------------------+g


To log a value change, overload `write` like this
(for zip field on res.partner model):

.. code-block:: python

    class ResPartner(models.Model):
        _inherit = "res.partner"

        @api.multi
        def write(self, vals):
            if "zip" in vals:
                self.env["value.log"].create(
                    {
                        "model": "res.partner",
                        "field": "zip",
                        "record_id", self.id,
                        "previous_value": str(self.zip),
                        "new_value": str(vals.get("zip")),
                    }
                )
            return super(ResPartner, self).write(vals)

If you need to log a value on creation, overwrite `create(vals)`.
