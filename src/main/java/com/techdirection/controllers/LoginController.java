package com.techdirection.controllers;


import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class LoginController {
    @GetMapping("/")

    public String landpage(){
        return "redirect:/login/login.html";
    }




}




