/*
 * Copyright 2020-2022 NXP
 * All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */

#include "board_init.h"
#include "demo_config.h"
#include "demo_info.h"
#include "fsl_debug_console.h"
#include "audio.h"
#include "model.h"
#include "output_postproc.h"
#include "timer.h"

#include "fsl_device_registers.h"
#include "pin_mux.h"
#include "clock_config.h"
#include "board.h"

#include "output_postproc.h"

//UART6 header
#include "fsl_lpuart.h"

//UART6 Definition
#define DEMO_LPUART          LPUART1
#define DEMO_LPUART_CLK_FREQ BOARD_DebugConsoleSrcFreq()

#define DEMO_LPUART6          LPUART6
#define DEMO_LPUART_CLK_FREQ6 BOARD_DebugConsoleSrcFreq()


int main(void)
{
    BOARD_Init();
    TIMER_Init();

    //UART6_init
	uint8_t result;
	uint8_t result_buff[2] = {0};
	bool flag = true;
	uint8_t pre_result = 255;
	lpuart_config_t config;

	//LED count
	int led_count = 0;

	BOARD_ConfigMPU();
	BOARD_InitBootPins();
	BOARD_InitBootClocks();
	BOARD_InitDebugConsole();

    DEMO_PrintInfo();

    //UART6 application
	LPUART_GetDefaultConfig(&config);
	config.baudRate_Bps = BOARD_DEBUG_UART_BAUDRATE;
	config.enableTx     = true;
	config.enableRx     = true;

	LPUART_Init(DEMO_LPUART, &config, DEMO_LPUART_CLK_FREQ); //Teraterm
	LPUART_Init(DEMO_LPUART6, &config, DEMO_LPUART_CLK_FREQ6); //Wemos

    //    int result = 12;

    if (MODEL_Init() != kStatus_Success)
    {
        PRINTF("Failed initializing model" EOL);
        for (;;) {}
    }

    tensor_dims_t inputDims;
    tensor_type_t inputType;
    uint8_t* inputData = MODEL_GetInputTensorData(&inputDims, &inputType);

    tensor_dims_t outputDims;
    tensor_type_t outputType;
    uint8_t* outputData = MODEL_GetOutputTensorData(&outputDims, &outputType);

    while (1)
    {
        /* Expected tensor dimensions: [batches, frames, mfcc, channels] */
        if (AUDIO_GetSpectralSample(inputData, inputDims.data[1] * inputDims.data[2]) != kStatus_Success)
        {
            PRINTF("Failed retrieving input audio" EOL);
            for (;;) {}
        }

        auto startTime = TIMER_GetTimeInUS();
        MODEL_RunInference();
        auto endTime = TIMER_GetTimeInUS();

        result = MODEL_ProcessOutput(outputData, &outputDims, outputType, endTime - startTime);
		result_buff[0] = result;

		if(pre_result == result){
			flag = false;
		}
		else{
			flag = true;
		}

		if(flag){
			PRINTF("     test: %d" EOL, result);
			//UART6 transmit
			if(result != 10 && result != 11){
				USER_LED_TOGGLE();
				led_count = 0;
				LPUART_WriteBlocking(DEMO_LPUART6, result_buff, sizeof(result_buff) - 1);
			}
		}

		pre_result = result;

		led_count++;
//		PRINTF("count: %d" EOL, led_count);
		if(led_count == 5){
			USER_LED_TOGGLE();
			led_count = 6;
		}
    }
}
