"use client";

import CountUp from "react-countup";

export function AnimatedNumber({
  value,
  suffix = "",
  decimals = 0,
}: {
  value: number;
  suffix?: string;
  decimals?: number;
}) {
  return (
    <CountUp
      end={value}
      duration={0.9}
      decimals={decimals}
      suffix={suffix}
      preserveValue
    />
  );
}