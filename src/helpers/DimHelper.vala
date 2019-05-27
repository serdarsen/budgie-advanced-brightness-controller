/*
 * AdvancedBrightnessController 
 * This file is part of UbuntuBudgie
 * 
 * Author: Serdar ŞEN github.com/serdarsen
 * 
 * Copyright © 2018-2019 Ubuntu Budgie Developers
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 */

using AdvancedBrightnessController.Models;

namespace AdvancedBrightnessController.Helpers 
{
public class DimHelper
{

    public bool isAvailable {get; set;}
    public List<Dim> list;

    private SubprocessHelper subprocessHelper;
    private ConfigHelper configHelper;

    // private int noOfConnectedDev = 0;

    public DimHelper()
    {
        subprocessHelper = new SubprocessHelper();
        configHelper  = new ConfigHelper("budgie-advanced-brightness-controller", "dim");
        Load();
    }

    private void Load()
    {
        list = new List<Dim>();

        // Load Dims From Config
        var retrivedDimNames = new string[]{};
        var dimObjects = configHelper.Read();

        foreach (var obj in dimObjects) 
        {
            var properties = obj.split(" ");
            if(properties.length > 3)
            {
                var dim = new Dim();
                dim.Name = properties[0];
                retrivedDimNames += dim.Name;
                dim.MaxBrightness = properties[1].to_double();
                dim.Brightness = properties[2].to_double();
                dim.IsActive = properties[3].to_bool();

                //print(@"Load Dims From Config: %s, %s, %s, %s \n", dim.Name, dim.MaxBrightnessText, dim.BrightnessText, dim.IsActive.to_string());
                list.append(dim);
            }
        }

        // Load Dims From Device
        var dimsString = subprocessHelper.RunAndGetResult({"xrandr", "-q"});

        dimsString = dimsString._strip(); 
        if (dimsString == "")
        {
            return;
        }

        var lines = dimsString.split("\n");
        var connectedDeviceCount = 0;
        foreach (var line in lines)
        {
            line = line._strip();
            if(line != "")
            {
                var words = line.split(" ");
                foreach(var word in words)
                {
                    if (word == "connected"
                        && !strv_contains(retrivedDimNames, words[0]))
                    {
                        var dim = new Dim();
                        dim.Name = words[0]; 
                        dim.MaxBrightness = 100;
                        dim.Brightness = 100;
                    
                        if(connectedDeviceCount == 0)
                        {
                            dim.IsActive = true;
                        }
                        else
                        {
                            dim.IsActive = false;
                        }
                        list.append(dim);
                        
                        //print(@"Load Dims From Device: %s, %s, %s, %s \n", dim.Name, dim.MaxBrightnessText, dim.BrightnessText, dim.IsActive.to_string());
                        connectedDeviceCount++;
                    }
                }
            }
        }   

        if (list.length() > 0)
        {
            isAvailable = true;
        }
        else
        {
            isAvailable = false; 
        }
    }
    
    public void SetBrightness(string name, double brightness)
    {
        //print(@"DimHelper.SetBrightness: $name $brightness \n");
        var aOnePercentOfbrightness = brightness / 100;
        subprocessHelper.Run({"xrandr", "--output", @"$name", "--brightness", @"$aOnePercentOfbrightness"});
        Save();
    }

    public void SetActive(Dim dim)
    {
        list.foreach((dim)=>
        {
            dim.IsActive = false;
        });
        dim.IsActive = true;
        Save();
    }

    public void Save()
    {
        var data = new string[]{};
        list.foreach((dim)=> 
        {
            var name = dim.Name;
            var maxBrightness = dim.MaxBrightnessText;
            var brightness = dim.BrightnessText;
            var isActive = dim.IsActive;
            data += (@"$name $maxBrightness $brightness $isActive");
        });
        configHelper.Write(data);
    }
}
}