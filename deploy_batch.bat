@echo off
chcp 65001 > nul
cd /d C:\Users\ash_f\Desktop\python\sg-property-bot
type database\schema.sql | flyctl postgres connect nlkxjo5wgmloy93v
