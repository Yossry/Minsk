# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Cost Estimation for Material, Labour and Overheads',
    'version': '12.0.0.4',
    'category': 'Project',
    'summary': 'This apps helps to calculate Job Estimation for Materials, Labous and Overheads',
    'description': """
        Send Estimation to your Customers for materials, labour, overheads details in job estimation.
        Estimation for Jobs - Material / Labour / Overheads
        Material Esitmation
        Job estimation
        labour estimation
        Overheads estimation
        BrowseInfo developed a new odoo/OpenERP module apps.
        This module use for Real Estate Management, Construction management, Building Construction,
        Material Line on JoB Estimation
        Labour Lines on Job Estimation.
        Overhead Lines on Job Estimation.
        create Quotation from the Job Estimation.
        overhead on job estimation
        Construction Projects
        Job Work Estimation for Material Cost Labour cost Overheads Cost Odoo Apps
        Job Work Estimation for Material Cost Labour cost Overhead Cost Odoo Apps
        material cost estimation
        labour cost estimation
        overhead cost estimation
        job work order estimation
        This Odoo apps helps to calculate job cost and job work estimation for Material cost Labour cost Overheads Cost 
        which easily send to your Customers as total estimation for the job work order.
        This odoo apps helps for Project/analytic account job order costing calculation for Material Cost, 
        Labour cost and Overheads Cost. Based on this work order cost estimation user you can also able to create quotation 
        and sales order also its linked with job estimation sheet.
        manage Job order estomation approval workflow for manager and also send estimation to customer by email before apporval to start work order. 
        Budgets
        Notes
        job work estimation
        job order estimation
        estimation for job work
        estimation for job order
        estimation for budget job
        Materials
        Material Request For Job Orders
        Add Materials
        Job Orders
        Create Job Orders
        Job Order Related Notes
        Issues Related Project
        Vendors
        Vendors / Contractors

        Construction Management
        Construction Activity
        Construction Jobs
        Job Order Construction
        Job Orders Issues
        Job Order Notes
        Construction Notes
        Job Order Reports
        Construction Reports
        Job Order Note
        Construction app
        Project Report
        Task Report
        Construction Project - Project Manager
        real estate property
        propery management
        bill of material
        Material Planning On Job Order

        Bill of Quantity On Job Order
        Bill of Quantity construction
        Project job costing on manufacturing

Env??e Estimaci??n a sus Clientes para materiales, mano de obra, detalles de gastos generales en la estimaci??n del trabajo.
        Estimaci??n de trabajos: material / mano de obra / gastos generales
        Esitmation material
        Estimaci??n de trabajo
        estimaci??n laboral
        Estimaci??n de gastos generales
        BrowseInfo desarroll?? una nueva aplicaci??n de m??dulo odoo / OpenERP.
        Este uso del m??dulo para la gesti??n inmobiliaria, la gesti??n de la construcci??n, la construcci??n de edificios,
        L??nea de material en la estimaci??n de JoB
        L??neas laborales sobre estimaci??n laboral.
        L??neas a??reas en la estimaci??n del trabajo.
        crear oferta de la estimaci??n del trabajo.
        sobrecarga en la estimaci??n del trabajo
        Proyectos de construcci??n
        Presupuestos
        Notas
        Materiales
        Solicitud de material para ??rdenes de trabajo
        Agregar materiales
        ??rdenes de trabajo
        Crear ??rdenes de trabajo
        Notas relacionadas con la orden de trabajo
        Temas relacionados Proyecto
        Vendedores
        Vendedores / Contratistas

        Gesti??n de la construcci??n
        Actividad de construcci??n
        Trabajos de construcci??n
        Construcci??n de ??rdenes de trabajo
        Problemas de pedidos de trabajo
        Notas de la orden de trabajo
        Notas de construcci??n
        Informes de ??rdenes de trabajo
        Informes de construcci??n
        Nota de orden de trabajo
        Aplicaci??n de construcci??n
        Informe del proyecto
        Informe de tareas
        Proyecto de construcci??n - Gerente de proyecto
        propiedad de bienes ra??ces
        gesti??n de la propiedad
        lista de materiales
        Planificaci??n de material en orden de trabajo

        Factura de cantidad en orden de trabajo
        Proyecto de ley de cantidad
        Costo del trabajo del proyecto en la fabricaci??n

1562/5000
Envoyer l'estimation ?? vos clients pour les mat??riaux, le travail, les d??tails de frais g??n??raux dans l'estimation du travail.
        Estimation pour les emplois - Mat??riel / main-d'??uvre / frais g??n??raux
        Esitmation mat??rielle
        Estimation du travail
        estimation du travail
        Estimation des frais g??n??raux
        BrowseInfo a d??velopp?? une nouvelle application de module odoo / OpenERP.
        Ce module d'utilisation pour la gestion immobili??re, la gestion de la construction, la construction de b??timents,
        Ligne de mat??riau sur Estimation JoB
        Lignes de main-d'??uvre sur l'estimation du travail.
        Lignes a??riennes sur l'estimation du travail.
        cr??er une citation ?? partir de l'estimation du travail.
        frais g??n??raux sur l'estimation du travail
        Projets de construction
        Budgets
        Remarques
        Mat??riaux
        Demande de mat??riel pour les commandes d'emploi
        Ajouter des mat??riaux
        Commandes d'emploi
        Cr??er des commandes d'emploi
        Notes relatives ?? la commande d'emploi
        Probl??mes li??s au projet
        Vendeurs
        Vendeurs / Entrepreneurs

        Gestion de la construction
        Activit?? de construction
        Emplois en construction
        Construction d'une commande d'emploi
        Probl??mes d'ordres de travail
        Notes de commande de travail
        Notes de construction
        Rapports de commande
        Rapports de construction
        Note de commande
        Application de construction
        Rapport de projet
        Rapport de t??che
        Projet de construction - Gestionnaire de projet
        propri??t?? immobili??re
        gestion de la propri??t??
        nomenclature
        Planification mat??rielle sur l'ordre de travail

        Projet de loi sur la commande
        Projet de loi de la quantit??
        Projet de travail co??tant sur la fabrication
    
""",
    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    'depends': ['sale_management','project','account','hr_timesheet','mail','stock'],
    'data': [
            'security/ir.model.access.csv',
            'report/job_estimate_report.xml',
            'report/job_estimate_report_view.xml',
            'data/ir_sequence_data.xml',
            'data/mail_template_data.xml',
            'views/custom_job_estimate_view.xml',
    ],
    "price": 39,
    "currency": 'EUR',
    'installable': True,
    'auto_install': False,
    "live_test_url":'https://youtu.be/f-3f4DwaOnM',
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
