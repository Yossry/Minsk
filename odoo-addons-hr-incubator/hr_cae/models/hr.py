# Copyright 2019 Coop IT Easy SCRL fs
#   Manuel Claeys Bouuaert <manuel@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class OriginStatus(models.Model):
    _name = "hr.origin.status"
    _description = "Origin Status"

    name = fields.Char()


class OriginStatusDetails(models.Model):
    _name = "hr.origin.status.details"
    _description = "Origin Status Details"

    name = fields.Char()
    origin_status_id = fields.Many2one(
        comodel_name="hr.origin.status", string="Origin Status", required=False
    )


class Role(models.Model):
    _name = "hr.coop.role"
    _description = "Role in Cooperative"

    name = fields.Char()


class SocialInsurance(models.Model):
    _name = "hr.social.insurance"
    _description = "Social Insurance"

    name = fields.Char()


class MutualInsurance(models.Model):
    _name = "hr.mutual.insurance"
    _description = "Mutual Insurance"

    name = fields.Char()


class MutualInsuranceLevel(models.Model):
    _name = "hr.mutual.insurance.level"
    _description = "Mutual Insurance Level"

    name = fields.Char()


class TransportMode(models.Model):
    _name = "hr.transport.mode"
    _description = "Transport Mode"

    name = fields.Char()


class ProfessionalLiability(models.Model):
    _name = "hr.professional.liability"
    _description = "Professional Liabilitie"

    name = fields.Char()


class Sector(models.Model):
    _name = "hr.sector"
    _description = "Sector"

    name = fields.Char()
