/*
 * AdvancedBrightnessController 
 * This file is part of UbuntuBudgie
 * 
 * Author: Serdar ŞEN github.com/serdarsen
 * 
 * Copyright © 2015-2017 Budgie Desktop Developers
 * Copyright © 2018-2019 Ubuntu Budgie Developers
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 */

using AdvancedBrightnessController.Widgets;

namespace AdvancedBrightnessController
{ 
public class Applet : Budgie.Applet
{
    private IndicatorButton indicatorButton;
    private Popover popover;
    private unowned Budgie.PopoverManager? manager = null;

    public Applet()
    {
        indicatorButton = new IndicatorButton();
        popover = new Popover(indicatorButton, 140, 300);        AddPressEventToIndicatorButton();
        add(indicatorButton);
        show_all();
    }

    public void AddPressEventToIndicatorButton()
    {
        indicatorButton.button_press_event.connect((e)=> 
        {
            if (e.button != 1) 
            {
                return Gdk.EVENT_PROPAGATE;
            }
            if (popover.get_visible()) 
            {
                popover.hide();
            } 
            else 
            {
                ShowPopover();
            }
            return Gdk.EVENT_STOP;
        });
    }

    public void ShowPopover()
    {
        this.manager.show_popover(indicatorButton);
    }

    /*Update popover*/
    public override void update_popovers(Budgie.PopoverManager? manager)
    {
        this.manager = manager;
        manager.register_popover(indicatorButton, popover);
    }
}

public class Plugin : Budgie.Plugin, Peas.ExtensionBase
{
    public Budgie.Applet get_panel_widget(string uuid)
    {
        return new Applet();
    }
}
}

[ModuleInit]
public void peas_register_types(TypeModule module)
{
    // boilerplate - all modules need this
    var objmodule = module as Peas.ObjectModule;
    objmodule.register_extension_type(typeof(Budgie.Plugin), typeof(AdvancedBrightnessController.Plugin));
}